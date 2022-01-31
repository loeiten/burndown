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


def save_sheet(path: Path, sheet_name: str, df: pd.DataFrame) -> None:
    """Store a dateframe to a sheet.

    Args:
        path (Path): Path to excel file to store sheet to
        sheet_name (str): Name of sheet
        df (pd.DataFrame): DataFrame to store
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
