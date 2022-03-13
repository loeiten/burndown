"""Module for storing and loading to excel."""

from pathlib import Path
from typing import List, Optional

import pandas as pd


def save_sheet(df_to_save: pd.DataFrame, path: Path, sheet_name: str) -> None:
    """Store a dateframe to a sheet.

    Args:
        df_to_save (pd.DataFrame): DataFrame to store
        path (Path): Path to excel file to store sheet to
        sheet_name (str): Name of sheet
    """
    print(f"Saving sheet '{sheet_name}' to: {path}")
    writer = pd.ExcelWriter(
        path, engine="openpyxl", mode="a", if_sheet_exists="replace"
    )
    df_to_save.to_excel(writer, sheet_name=sheet_name)
    writer.save()


def read_sheet(
    path: Path,
    sheet_name: str,
    index_col: Optional[str],
    usecols: Optional[List] = None,
) -> pd.DataFrame:
    """Load a dataframe from a sheet.

    Args:
        path (Path): Path to excel file to load from
        sheet_name (str): Name of sheet
        index_col (str): Column to use as index
        usecols (Optional[List], optional): Columns to parse. Defaults to None.

    Returns:
        pd.DataFrame: Content of sheet
    """
    return pd.read_excel(
        str(path),
        sheet_name=sheet_name,
        index_col=index_col,
        usecols=usecols,
        date_parser=lambda col: pd.to_datetime(col, format="%Y-%m-%d").date(),
    )
