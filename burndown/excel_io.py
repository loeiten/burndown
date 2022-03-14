"""Module for storing and loading to excel."""

from pathlib import Path
from typing import Dict, List, Optional, Union

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
    sheet_name: Optional[str] = None,
    index_col: Optional[str] = None,
    usecols: Optional[List] = None,
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Load a dataframe from a sheet.

    Args:
        path (Path): Path to excel file to load from
        sheet_name (Optional[str], optional): Name of sheet. Defaults to None.
        index_col (Optional[str], optional): Column to use as index. Defaults to None.
        usecols (Optional[List], optional): Columns to parse. Defaults to None.

    Returns:
        Union[pd.DataFrame, Dict[str, pd.DataFrame]]: Content of sheet(s)
    """
    return pd.read_excel(
        str(path), sheet_name=sheet_name, index_col=index_col, usecols=usecols
    )
