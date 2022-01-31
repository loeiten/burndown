from burndown.burndown import save_sheet, get_ideal_burndown
from burndown.sprint_dates import SprintDates
import pandas as pd
from pathlib import Path
import argparse


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

    df = pd.DataFrame(
        {
            "date": sprint_dates.dates,
            "ideal_burndown": ideal_burndown,
            "remaining": remaining,
        }
    )
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)

    save_sheet(sheet_path, sheet_name, df)


if __name__ == "__main__":
    date = pd.to_datetime("today")
    root_path = Path(__file__).parents[1].resolve()

    sheet_dir = root_path.joinpath("data")
    sheet_dir.mkdir(parents=True, exist_ok=True)
    sheet_path = sheet_dir.joinpath("burndown.xlsx")

    parser = argparse.ArgumentParser(description="Start a sprint.")
    parser.add_argument("-r", "--release", type=str, help="Release number")
    parser.add_argument("-s", "--sprint_number", type=str, help="Sprint number")
    parser.add_argument(
        "-p",
        "--storypoints_start",
        type=int,
        help="Number of storypoints at sprint start",
    )
    parser.add_argument(
        "-l",
        "--length",
        default=14,
        type=int,
        help="Number of days in the sprint (including week-ends)",
    )
    parser.add_argument(
        "-d",
        "--days_off",
        nargs="+",
        type=str,
        help="Days without development on the form yyyy-mm-dd (week-ends are inferred)",
    )

    args = parser.parse_args()

    days_off = (
        [pd.to_datetime(date) for date in args.days_off]
        if args.days_off is not None
        else None
    )
    sprint_dates = SprintDates(date, args.length, days_off)

    sheet_name = f"{args.release}-{args.sprint_number}"

    start_new_sprint(
        sheet_path=sheet_path,
        sheet_name=sheet_name,
        sprint_dates=sprint_dates,
        storypoints_start=args.storypoints_start,
    )
