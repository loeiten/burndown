"""Module containing the SprintTask class."""

from pathlib import Path
from typing import Dict, Optional, Union

import numpy as np
import pandas as pd
from pandas import Timestamp
from datetime import date

from burndown.excel_io import read_sheet


class SprintTasks:
    """Class for data analysis of the sprint tasks data."""

    def __init__(self, sprint_tasks_path: Path, burndown_path: Path) -> None:
        """
        Load the data to the object.

        Args:
            sprint_tasks_path (Path): Path to the spreadsheet containing the creeps
            burndown_path (Path): Path to the spreadsheet containing the burndown
        """
        # Read all the sheets in burndown in order to obtain the dates
        self.burndown_sheets = read_sheet(
            burndown_path, sheet_name=None, index_col=None, usecols=["date", "ideal_burndown"]
        )

        # Set the date to date
        for sprint_name in self.burndown_sheets.keys():
            self.burndown_sheets[sprint_name].loc[:, "date"] = (
                self.burndown_sheets[sprint_name].loc[:, "date"].dt.date
            )
            self.burndown_sheets[sprint_name].set_index("date", inplace=True)

        # Read all the sheets in sprint_tasks
        self.sprint_tasks_sheets = read_sheet(
            sprint_tasks_path,
            sheet_name=None,
            index_col=None,
            usecols=[
                "burned",
                "creep_date",
                "creep",
                "creep_category",
                "category",
                "Date Closed",
                "Original estimate",
                "Points",
            ],
        )

        # Remove bad rows and set the dates to date
        for sprint_name in self.sprint_tasks_sheets.keys():
            # Drop any row where "category" is NaN (for example the sum row)
            self.sprint_tasks_sheets[sprint_name] = self.sprint_tasks_sheets[
                sprint_name
            ][self.sprint_tasks_sheets[sprint_name]["category"].notna()]

            # Set the dates to date
            try:
                self.sprint_tasks_sheets[sprint_name].loc[:, "creep_date"] = (
                    self.sprint_tasks_sheets[sprint_name].loc[:, "creep_date"].dt.date
                )
            except AttributeError:
                # In case there are no dates, pandas will throw an error
                pass
            try:
                self.sprint_tasks_sheets[sprint_name].loc[:, "Date Closed"] = (
                    self.sprint_tasks_sheets[sprint_name].loc[:, "Date Closed"].dt.date
                )
            except AttributeError:
                # In case there are no dates, pandas will throw an error
                pass

        # Create sprint planning DataFrames (contains what was agreed upon during sprint planning)
        self.sprint_planning_dfs = dict()
        for sprint_name in self.sprint_tasks_sheets.keys():
            sprint_df = self.sprint_tasks_sheets[sprint_name].copy()
            # In the case of re-estimation, we will split points between sprint planning and creep
            # To facilitate this we set the creep of this column to zero ....
            sprint_df.loc[
                sprint_df.loc[:, "creep_category"] == "Re-estimation", "creep"
            ] = 0
            # ...and set the burn to the original points
            sprint_df.loc[
                (sprint_df.loc[:, "creep_category"] == "Re-estimation")
                & ~(np.isclose(sprint_df.loc[:, "burned"], 0)),
                "burned",
            ] = sprint_df.loc[
                (sprint_df.loc[:, "creep_category"] == "Re-estimation")
                & ~(np.isclose(sprint_df.loc[:, "burned"], 0)),
                "Original estimate",
            ]

            sprint_df = sprint_df.loc[np.isclose(sprint_df.loc[:, "creep"], 0)]
            sprint_df.drop(
                columns=["creep", "creep_category", "creep_date"], inplace=True
            )
            self.sprint_planning_dfs[sprint_name] = sprint_df

        # Create creep DataFrames
        self.creep_dfs = dict()
        for sprint_name in self.sprint_tasks_sheets.keys():
            creep_df = self.sprint_tasks_sheets[sprint_name].copy()
            # In the case of re-estimation, we will split points between sprint planning and creep
            # To facilitate this we set the burn to the creep
            creep_df.loc[
                (creep_df.loc[:, "creep_category"] == "Re-estimation")
                & ~(np.isclose(creep_df.loc[:, "burned"], 0)),
                "burned",
            ] = creep_df.loc[
                (creep_df.loc[:, "creep_category"] == "Re-estimation")
                & ~(np.isclose(creep_df.loc[:, "burned"], 0)),
                "creep",
            ]

            creep_df = creep_df.loc[~np.isclose(creep_df.loc[:, "creep"], 0)]
            creep_df.loc[:, "date"] = creep_df.loc[:, "creep_date"]
            creep_df.drop(columns="creep_date", inplace=True)
            self.creep_dfs[sprint_name] = creep_df

        # Create category DataFrames
        self.category_dfs = dict()
        for sprint_name in self.sprint_tasks_sheets.keys():
            self.category_dfs[sprint_name] = self.sprint_tasks_sheets[
                sprint_name
            ].copy()

    def get_total_sprint_creep_and_burn(self) -> Dict[str, pd.DataFrame]:
        """
        Get the DataFrames containing the total creep and burn of the sprint.

        Returns:
           Dict[str, pd.DataFrame]:
            Dict containing the DataFrames containing the total creep and burn of the sprint
        """
        total_sprint_burn_dfs = dict()
        for sprint_name in self.sprint_tasks_sheets.keys():
            # Sum the creeps
            creep_df = self.creep_dfs[sprint_name].groupby("date")[["creep"]].sum()

            # Copy sprint task sheet
            burn_df = self.sprint_tasks_sheets[sprint_name].loc[
                :, ["Date Closed", "burned"]
            ]

            # Make a date column out of burn_df
            burn_df.loc[:, "date"] = burn_df.loc[:, "Date Closed"]
            # Remove the creep_date
            burn_df.drop(columns="Date Closed", inplace=True)
            burn_df.dropna(inplace=True)

            # Sum the burndown
            burn_df = burn_df.groupby("date")[["burned"]].sum()

            # Merge the dfs
            merged_df = pd.merge(
                self.burndown_sheets[sprint_name], burn_df, how="outer", on="date"
            )
            merged_df = pd.merge(merged_df, creep_df, how="outer", on="date")

            # Remove rows outside of sprint window
            merged_df = merged_df.loc[
                (merged_df.index <= burn_df.index.max())
                & (merged_df.index >= burn_df.index.min()),
                :,
            ]

            # Get the accumulated columns
            merged_df.loc[:, "accum_burned"] = (
                merged_df.loc[:, "burned"].fillna(0).cumsum()
            )
            merged_df.loc[:, "accum_creep"] = (
                merged_df.loc[:, "creep"].fillna(0).cumsum()
            )
            merged_df.drop(columns="burned", inplace=True)
            merged_df.drop(columns="creep", inplace=True)

            total_sprint_burn_dfs[sprint_name] = merged_df

        return total_sprint_burn_dfs

    def _get_categories(self, group_by: str, col: str) -> pd.DataFrame:
        """
        Get the DataFrame containing aggregated categories.

        In the DataFrame the entries are the sprint names and the columns are
        the different categories

        Returns:
            pd.DataFrame: The DataFrame of the categories.
        """
        categories = dict()
        for sprint_name in self.sprint_tasks_sheets.keys():
            categories[sprint_name] = (
                self.sprint_tasks_sheets[sprint_name].groupby(group_by)[[col]].sum().T
            )
            categories[sprint_name]["sprint"] = sprint_name
            categories[sprint_name].set_index("sprint", inplace=True)

        categories_df = pd.concat(
            [categories[sprint] for sprint in self.sprint_tasks_sheets.keys()]
        )
        categories_df.sort_index(inplace=True)
        categories_df.fillna(0, inplace=True)
        return categories_df

    def get_creep_categories(self) -> pd.DataFrame:
        """
        Get the DataFrame containing the creep categories.

        In the DataFrame the entries are the sprint names and the columns are
        the different categories

        Returns:
            pd.DataFrame: The DataFrame of the creep categories.
        """
        return self._get_categories(group_by="creep_category", col="creep")

    def get_burn_categories(self) -> pd.DataFrame:
        """
        Get the DataFrame containing the burn categories.

        In the DataFrame the entries are the sprint names and the columns are
        the different categories

        Returns:
            pd.DataFrame: The DataFrame of the creep categories.
        """
        category_df = self._get_categories(group_by="category", col="burned")
        category_df.drop("Duplicate", axis=1, inplace=True)
        return category_df

    def get_sprint_planning_burn(
        self, sprint_name: str, until_date: Optional[Timestamp] = None
    ) -> pd.DataFrame:
        """Get the sprint burndown.

        NOTE: Burn on the sprint start day is first counted on the next day to
              fix the points in the sprint start.

        Args:
            sprint_name (str): Name of the sprint
            until_date (Optional[Timestamp]): The date to calculate the creep until. Defaults to None

        Returns:
            pd.DataFrame: The sprint burndown consisting of remaining points and dates
        """
        # FIXME: Enable the until_date timestamp
        sprint_df = self.sprint_planning_dfs[sprint_name]
        # Get the number of points as they were during sprint_planning
        start_points = sprint_df["Original estimate"].sum()
        sprint_dates = self.burndown_sheets[sprint_name].index
        burn_dict = {"date": [], "remaining": []}
        sprint_start = min(sprint_dates)
        for date in sprint_dates:
            burn_dict["date"].append(date)
            # NOTE: We fix the first day to the sprint planning
            #       If anything is burned on this day it will first count the next day
            if date == sprint_start:
                burn_dict["remaining"].append(start_points)
            else:
                burn_dict["remaining"].append(
                    start_points
                    - sprint_df.loc[sprint_df.loc[:, "Date Closed"] <= date, "burned"].sum()
                )

        sprint_planning_burn_df = pd.DataFrame(burn_dict)
        sprint_planning_burn_df.set_index("date", inplace=True)
        return sprint_planning_burn_df

    def get_creep_burn(
        self, sprint_name: str, until_date: Optional[Timestamp] = None
    ) -> pd.DataFrame:
        """Get the creep burndown.

        NOTE: Burn on the sprint start day is first counted on the next day to
              fix the points in the sprint start.

        Args:
            sprint_name (str): Name of the sprint
            until_date (Optional[Timestamp]): The date to calculate the creep until. Defaults to None

        Returns:
            pd.DataFrame: The sprint creep burndown consisting of remaining points and dates
        """
        # FIXME: Enable the until_date timestamp
        creep_df = self.creep_dfs[sprint_name]
        sprint_dates = self.burndown_sheets[sprint_name].index
        burn_dict = {"date": [], "remaining": []}
        sprint_start = min(sprint_dates)
        for date in sprint_dates:
            burn_dict["date"].append(date)
            cur_day_df = creep_df.loc[creep_df.loc[:, "date"] <= date]
            creep_until_this_day = cur_day_df.loc[:, "creep"].sum()
            # NOTE: We fix the first day to the sprint planning
            #       If anything is burned on this day it will first count the next day
            if date == sprint_start:
                burn_dict["remaining"].append(creep_until_this_day)
            else:
                creep_burn_until_this_day = cur_day_df.loc[:, "burned"].sum()
                burn_dict["remaining"].append(
                    creep_until_this_day - creep_burn_until_this_day
                )

        creep_burn_df = pd.DataFrame(burn_dict)
        creep_burn_df.set_index("date", inplace=True)
        return creep_burn_df

    def get_daily_creep(self, sprint_name:str, until_date: Optional[Timestamp] = None) -> Dict[str, Union[date, str, float]]:
        """Get the types and points of creeps for the days in the sprint.

        Args:
            sprint_name (str): Name of the sprint
            until_date (Optional[Timestamp]): The date to calculate the creep until. Defaults to None

        Returns:
            Dict[str, Union[date, str, float]]: The sprint creep burndown consisting of remaining points and dates
        """
        creep_df = self.creep_dfs[sprint_name]
        daily_creep_dict = dict()
        daily_creep_dict["date"] = self.burndown_sheets[sprint_name].index.values
        # Initialize all categories
        creep_categories = creep_df.loc[:, "creep_category"].unique()
        for category in creep_categories:
            daily_creep_dict[category] = []

        for date in daily_creep_dict["date"]:
            creeps_cur_date = creep_df.loc[creep_df.loc[:, "date"] == date].groupby("creep_category")[["creep"]].sum()
            for category in creep_categories:
                if category in creeps_cur_date.index:
                    # As we have grouped by there will only be one index, hence the index of 0
                    daily_creep_dict[category].append(creeps_cur_date.loc[category].values[0])
                else:
                    daily_creep_dict[category].append(0)

        return daily_creep_dict

    def get_total_burn(self) -> pd.DataFrame:
        """
        Get the DataFrame containing the total burndown across several sprints.

        The entries of the DataFrame are different sprints
        The columns consist of
        - Total points burned
        - Total points burned which were present at the sprint planning
        - Percentage of points from the sprint planning which were burned

        Returns:
            pd.DataFrame: The DataFrame containing the total burndown.
        """
        burndowns = dict()
        for sprint_name in self.sprint_tasks_sheets.keys():
            burndown_dict = dict()
            burndown_dict["total_points"] = (
                self.sprint_tasks_sheets[sprint_name].loc[:, "burned"].sum()
            )
            sprint_start_points = self.sprint_tasks_sheets[sprint_name].loc[
                (self.sprint_tasks_sheets[sprint_name].loc[:, "creep_category"].isna())
                & (
                    self.sprint_tasks_sheets[sprint_name].loc[:, "creep_category"]
                    != "Re-estimation"
                ),
                ["Points", "burned"],
            ]
            burndown_dict["sprint_start_burned"] = sprint_start_points.loc[
                :, "burned"
            ].sum()
            burndown_dict["achievement"] = (
                100
                * burndown_dict["sprint_start_burned"]
                / sprint_start_points.loc[:, "Points"].sum()
            )
            burndowns[sprint_name] = pd.DataFrame(burndown_dict, index=[sprint_name])

        burndown = pd.concat(
            [burndowns[sprint] for sprint in self.sprint_tasks_sheets.keys()]
        )
        burndown.sort_index(inplace=True)
        burndown.fillna(0, inplace=True)
        return burndown
