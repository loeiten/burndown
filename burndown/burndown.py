"""Module containing functions for the sprint burndown."""

import argparse
from pathlib import Path
from typing import List

import pandas as pd

from burndown.excel_io import read_sheet, save_sheet
from burndown.sprint_dates import SprintDates


def get_ideal_burndown(
    sprint_dates: SprintDates, storypoints_start: int
) -> List[float]:
    """Get the ideal burndown.

    Args:
        sprint_dates (SprintDates): Sprint dates object
        storypoints_start (int): How many storypoints as start

    Returns:
        List[float]: The ideal burndown values
    """
    # Minus 1 one since we will not expect burn the first day
    ideal_rate = -storypoints_start / (sprint_dates.days_of_development - 1)
    ideal_burndown = list()
    current_storypoint = storypoints_start
    ideal_burndown.append(current_storypoint)
    for date in sprint_dates.dates[1:]:
        if date not in sprint_dates.dates_witout_development:
            current_storypoint += ideal_rate

        ideal_burndown.append(current_storypoint)
    return ideal_burndown


if __name__ == "__main__":
    root_path = Path(__file__).parents[1].resolve()
    sheet_dir = root_path.joinpath("data")
    sheet_path = sheet_dir.joinpath("burndown.xlsx")

    with pd.ExcelFile(str(sheet_path)) as xl:
        sheet_name = xl.sheet_names[0]

    df_to_save = read_sheet(sheet_path, sheet_name=sheet_name, index_col="date")

    parser = argparse.ArgumentParser(
        description="Add storypoints for the current sheet."
    )
    parser.add_argument("-p", "--story_points", type=str, help="Remaining story points")
    parser.add_argument(
        "-d", "--date", default=None, type=str, help="Date on the form yyyy-mm-dd"
    )
    args = parser.parse_args()

    date_ = (
        pd.to_datetime(args.date) if args.date is not None else pd.to_datetime("today")
    )
    df_to_save.loc[date_.normalize(), "remaining"] = args.story_points

    save_sheet(df_to_save=df_to_save, path=sheet_path, sheet_name=sheet_name)
