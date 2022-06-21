"""Script for plotting agile maturity."""

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

from burndown.excel_io import read_sheet
from survey.plots import plot_agile_maturity


def extract_float_from_level_str(string: str) -> float:
    r"""Extract float from strings on the form LEVEL \d.*.

    Args:
        string (str): String to extract float from

    Returns:
        np.float: Float returned
    """
    search_obj = re.search(r"LEVEL (\d)", string)
    if search_obj is not None:
        result = float(search_obj.group(1))
    else:
        result = np.nan
    return result


def get_agile_maturity(sheet_path: Path) -> pd.DataFrame:
    """Return the agile maturity data frame

    Args:
        sheet_path (Path): Path to the sheet containing the agile maturity

    Returns:
        pd.DataFrame: The agile maturity data frame
    """
    raw_dfs = read_sheet(sheet_path)

    # Get the columns of the first df
    all_columns = raw_dfs[list(raw_dfs.keys())[0]].columns
    columns_map = {}
    for original_column in all_columns:
        column = original_column.replace(":", "")
        words = column.split(" ")
        dimension = []
        for word in words:
            if word.isupper():
                dimension.append(word)
            else:
                continue

        if len(dimension) != 0:
            columns_map[original_column] = " ".join(dimension).capitalize()

    # Initialize the dict to create the df from
    agile_dict = {"Sprint": []}
    for _, dimension in columns_map.items():
        agile_dict[dimension] = []

    # Populate the agile_dict
    for sprint_name, raw_df in raw_dfs.items():
        agile_dict["Sprint"].append(sprint_name)
        for original_column, dimension in columns_map.items():
            raw_df.loc[:, original_column] = raw_df.loc[:, original_column].apply(
                extract_float_from_level_str
            )
            agile_dict[dimension].append(raw_df.loc[:, original_column].mean())

    agile_maturity_df = pd.DataFrame(agile_dict)
    agile_maturity_df.set_index("Sprint", inplace=True)
    return agile_maturity_df


def main() -> None:
    """Plot and save the agile maturity."""
    root_path = Path(__file__).parents[1].resolve()
    charts_dir = root_path.joinpath("charts")
    sheet_dir = root_path.joinpath("data")

    charts_dir.mkdir(parents=True, exist_ok=True)

    argparse.ArgumentParser(description="Plot the agile maturity.")

    sheet_path = sheet_dir.joinpath("agile_maturity.xlsx")
    agile_maturity_df = get_agile_maturity(sheet_path=sheet_path)

    plot_agile_maturity(agile_maturity_df=agile_maturity_df, save_dir=charts_dir)


if __name__ == "__main__":
    main()
