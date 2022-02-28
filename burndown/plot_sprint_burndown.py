"""Script for plotting the day to day burndown."""

import argparse
from pathlib import Path

import pandas as pd

from burndown.excel_io import read_sheet
from burndown.plots import plot_burndown
from burndown.sprint_dates import SprintDates


def main() -> None:
    """Plot the burndown and categories of this sprint."""
    root_path = Path(__file__).parents[1].resolve()
    charts_dir = root_path.joinpath("charts")
    sheet_dir = root_path.joinpath("data")

    charts_dir.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description="Plot burndown chart.")
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

    sheet_path = sheet_dir.joinpath("burndown.xlsx")
    sheet_name = f"{args.release}-{args.sprint_number}"

    burndown_df = read_sheet(sheet_path, sheet_name, index_col="date")
    days_off = (
        [pd.to_datetime(date) for date in args.days_off]
        if args.days_off is not None
        else None
    )
    sprint_dates = SprintDates(burndown_df.index[0], len(burndown_df.index), days_off)

    plot_burndown(burndown_df, sprint_dates, charts_dir, sheet_name)


if __name__ == "__main__":
    main()
