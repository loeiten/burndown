from typing import Tuple
import argparse
import pandas as pd
from burndown.sprint_dates import SprintDates
from burndown.excel_io import read_sheet
from burndown.plot import plot_total_burn_and_creep, plot_creep_categories
from pathlib import Path


def get_burn_down_creep_and_categories(creep_path: Path, burndown_path: Path, sheet_name: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return the dfs of accumulated burndown, accumulated creep and creep categories.

    Args:
        creep_path (Path): Path to the spreadsheet containing the creeps
        burndown_path (Path): Path to the spreadsheet containing the burndown
        sheet_name (str): Name of the sheet to load from

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Tuple containing

          merged_df (pd.DataFrame): The dataframe containing the accumulated burndown and creep
          category_df (pd.DataFrame): The dataframe containing the creep categories
    """
    # Get the dates
    burndown_df = read_sheet(burndown_path, sheet_name=sheet_name, index_col=None, usecols=['date'])
    # Set date to date
    burndown_df.loc[:, "date"] = burndown_df.loc[:, "date"].dt.date
    burndown_df.set_index("date", inplace=True)

    # Get the creeps
    creep_df = read_sheet(creep_path, sheet_name=sheet_name, index_col=None, usecols=['creep_date', 'creep', 'category'])
    # Cast creep_date to a date
    creep_df.loc[:, "creep_date"] = creep_df.loc[:, "creep_date"].dt.date
    # Make a date column out of creep_date
    creep_df.loc[:, "date"] = creep_df.loc[:, "creep_date"]
    # Remove the creep_date
    creep_df.drop(columns="creep_date", inplace=True)
    creep_df.dropna(inplace=True)

    # Extract the category df
    category_df = creep_df.groupby('category')[['creep']].sum()
    creep_df.drop(columns="category", inplace=True)

    # Sum the creeps
    creep_df = creep_df.groupby('date')[['creep']].sum()

    # Get the burns
    burn_df = read_sheet(creep_path, sheet_name=sheet_name, index_col=None, usecols=['Date Closed', 'burned'])
    # Cast burn_df to a date
    burn_df.loc[:, "Date Closed"] = burn_df.loc[:, "Date Closed"].dt.date
    # Make a date column out of burn_df
    burn_df.loc[:, "date"] = burn_df.loc[:, "Date Closed"]
    # Remove the creep_date
    burn_df.drop(columns="Date Closed", inplace=True)
    burn_df.dropna(inplace=True)

    # Sum the burndown
    burn_df = burn_df.groupby('date')[['burned']].sum()

    # Merge the dfs
    merged_df = pd.merge(burndown_df, burn_df, how="outer", on="date")
    merged_df = pd.merge(merged_df, creep_df, how="outer", on="date")

    # Remove rows outside of sprint window
    merged_df = merged_df.loc[(merged_df.index <= burndown_df.index.max()) & (merged_df.index >= burndown_df.index.min()) ,:]

    # Get the accumulated columns
    merged_df.loc[:, "accum_burned"] = merged_df.loc[:, "burned"].fillna(0).cumsum()
    merged_df.loc[:, "accum_creep"] = merged_df.loc[:, "creep"].fillna(0).cumsum()
    merged_df.drop(columns="burned", inplace=True)
    merged_df.drop(columns="creep", inplace=True)
    return merged_df, category_df


if __name__ == "__main__":
    root_path = Path(__file__).parents[1].resolve()
    charts_dir = root_path.joinpath("charts")
    sheet_dir = root_path.joinpath("data")
    creep_path = sheet_dir.joinpath("creeps.xlsx")
    burndown_path = sheet_dir.joinpath("burndown.xlsx")

    parser = argparse.ArgumentParser(
        description="Plot the total burned storypoints and creeps."
    )
    parser.add_argument("-r", "--release", type=str, help="Release number")
    parser.add_argument("-s", "--sprint_number", type=str, help="Sprint number")
    parser.add_argument(
        "-d",
        "--days_off",
        nargs="+",
        type=str,
        help="Days without development on the form yyyy-mm-dd (week-ends are inferred)",
    )
    args = parser.parse_args()

    sheet_name = f"{args.release}-{args.sprint_number}" 

    merged_df, categories_df = get_burn_down_creep_and_categories(creep_path, burndown_path, sheet_name)

    days_off = (
        [pd.to_datetime(date) for date in args.days_off]
        if args.days_off is not None
        else None
    )
    sprint_dates = SprintDates(merged_df.index[0], len(merged_df.index), days_off)

    plot_total_burn_and_creep(merged_df, sprint_dates, charts_dir, sheet_name)
    plot_creep_categories(categories_df, charts_dir, sheet_name)