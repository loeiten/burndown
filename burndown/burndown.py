import argparse
from typing import List
import pandas as pd
from burndown.sprint_dates import SprintDates
from pathlib import Path


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
    ideal_rate = -storypoints_start / sprint_dates.days_of_development
    ideal_burndown = list()
    current_storypoint = storypoints_start
    ideal_burndown.append(current_storypoint)
    for date in sprint_dates.dates[1:]:
        if date not in sprint_dates.dates_witout_development:
            current_storypoint += ideal_rate

        ideal_burndown.append(current_storypoint)
    return ideal_burndown


def save_sheet(df: pd.DataFrame, path: Path, sheet_name: str) -> None:
    """Store a dateframe to a sheet.

    Args:
        df (pd.DataFrame): DataFrame to store
        path (Path): Path to excel file to store sheet to
        sheet_name (str): Name of sheet
    """
    print(f"Saving sheet '{sheet_name}' to: {path}")
    writer = pd.ExcelWriter(path, engine="xlsxwriter")
    df.to_excel(writer, sheet_name=sheet_name)
    writer.save()


def read_sheet(path: Path, sheet_name: str) -> pd.DataFrame:
    """Load a dataframe from a sheet.

    Args:
        path (Path): Path to excel file to load from
        sheet_name (str): Name of sheet

    Returns:
        pd.DataFrame: Content of sheet
    """
    return pd.read_excel(str(path), sheet_name=sheet_name, index_col="date")


if __name__ == "__main__":
    root_path = Path(__file__).parents[1].resolve()
    sheet_dir = root_path.joinpath("data")
    sheet_path = sheet_dir.joinpath("burndown.xlsx")

    with pd.ExcelFile(str(sheet_path)) as xl:
        sheet_name = xl.sheet_names[0]

    read_sheet(sheet_path, sheet_name=sheet_name)
    df = pd.read_excel(str(sheet_path), index_col="date")

    parser = argparse.ArgumentParser(
        description="Add storypoints for the current sheet."
    )
    parser.add_argument("-p", "--story_points", type=str, help="Remaining story points")
    parser.add_argument(
        "-d", "--date", default=None, type=str, help="Date on the form yyyy-mm-dd"
    )
    args = parser.parse_args()

    date = (
        pd.to_datetime(args.date) if args.date is not None else pd.to_datetime("today")
    )
    df.loc[date.normalize(), "remaining"] = args.story_points

    save_sheet(df=df, path=sheet_path, sheet_name=sheet_name)
