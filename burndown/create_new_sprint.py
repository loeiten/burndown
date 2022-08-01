"""Script for starting a new sprint."""

import argparse
from pathlib import Path

import pandas as pd

from burndown.burndown import get_ideal_burndown
from burndown.excel_io import save_sheet
from burndown.sprint_dates import SprintDates


def start_new_sprint(
    sheet_path: Path,
    sheet_name: str,
    sprint_dates: SprintDates,
    storypoints_start: int,
) -> None:
    """Start a new sprint.

    Will create a new sprint in the excel sheet pointed to by sheet_path.

    Args:
        sprint_dates (SprintDates): Sprint dates object
        storypoints_start (int): Number of storypoints planned after sprint planning
        sheet_path (Path): Path to the excel sheet
        sheet_name (str): Name of the sheet
        start_date (Timestamp): Start date of sprint
        sprint_length (int): Days planned for the sprint
    """
    ideal_burndown = get_ideal_burndown(sprint_dates, storypoints_start)
    remaining = [None for _ in range(len(sprint_dates.dates))]
    remaining[0] = storypoints_start

    burndown_df = pd.DataFrame(
        {
            "date": sprint_dates.dates,
            "ideal_burndown": ideal_burndown,
            "remaining": remaining,
        }
    )
    burndown_df["date"] = pd.to_datetime(burndown_df["date"])
    burndown_df.set_index("date", inplace=True)

    save_sheet(burndown_df, sheet_path, sheet_name)


if __name__ == "__main__":
    root_path = Path(__file__).parents[1].resolve()

    sheet_dir = root_path.joinpath("data")
    sheet_dir.mkdir(parents=True, exist_ok=True)
    sheet_path_ = sheet_dir.joinpath("burndown.xlsx")

    parser = argparse.ArgumentParser(description="Start a sprint.")
    parser.add_argument(
        "-r", "--release", type=str, help="Release number", required=True
    )
    parser.add_argument(
        "-s", "--sprint_number", type=str, help="Sprint number", required=True
    )
    parser.add_argument(
        "-p",
        "--storypoints_start",
        type=float,
        help="Number of storypoints at sprint start",
        required=True,
    )
    parser.add_argument(
        "-l",
        "--length",
        default=14,
        type=int,
        help="Number of days in the sprint (including week-ends)",
    )
    parser.add_argument(
        "-m",
        "--count_mid_day",
        default=True,
        type=bool,
        help="In case the sprint planning is during mid-day: Add one day to the end of the sprint. This day will not be considered in the ideal burn.",
    )
    parser.add_argument(
        "-d",
        "--start_date",
        type=str,
        help="Start date of sprint on form yyyy-mm-dd",
    )
    parser.add_argument(
        "-o",
        "--days_off",
        nargs="+",
        type=str,
        help="Days without development on the form yyyy-mm-dd (week-ends are inferred)",
    )

    args = parser.parse_args()

    if args.start_date is not None:
        date = pd.to_datetime(args.start_date)
    else:
        date = pd.to_datetime("today")

    days_off = (
        [pd.to_datetime(date) for date in args.days_off]
        if args.days_off is not None
        else list()
    )

    if args.count_mid_day:
        days_off.append((pd.to_datetime(date) + pd.DateOffset(args.length)).date())
        args.length += 1

    sprint_dates_ = SprintDates(date, args.length, days_off)

    sheet_name_ = f"{args.release}-{args.sprint_number}"

    start_new_sprint(
        sheet_path=sheet_path_,
        sheet_name=sheet_name_,
        sprint_dates=sprint_dates_,
        storypoints_start=args.storypoints_start,
    )
