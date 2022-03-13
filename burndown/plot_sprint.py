"""Script for plotting the metric for a specific sprint."""

import argparse
from pathlib import Path

import pandas as pd

from burndown.plots import (
    plot_sprint_burn_and_creep,
    plot_sprint_categories,
    plot_sprint_creep_categories,
)
from burndown.sprint_dates import SprintDates
from burndown.sprint_tasks import SprintTasks


def main() -> None:
    """
    Plot the total burn and creep together with the creep categories for a certain sprint.
    """
    root_path = Path(__file__).parents[1].resolve()
    charts_dir = root_path.joinpath("charts")
    sheet_dir = root_path.joinpath("data")
    sprint_tasks_path = sheet_dir.joinpath("sprint_tasks.xlsx")
    burndown_path = sheet_dir.joinpath("burndown.xlsx")

    sprint_tasks = SprintTasks(
        sprint_tasks_path=sprint_tasks_path, burndown_path=burndown_path
    )

    parser = argparse.ArgumentParser(description="Plot metrics specific for a sprint.")
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

    sprint_name = f"{args.release}-{args.sprint_number}"

    total_sprint_burn_dfs = sprint_tasks.get_total_sprint_creep_and_burn()
    burn_categories_df = sprint_tasks.get_burn_categories()
    creep_categories_df = sprint_tasks.get_creep_categories()

    burn_df = total_sprint_burn_dfs[sprint_name]

    days_off = (
        [pd.to_datetime(date) for date in args.days_off]
        if args.days_off is not None
        else None
    )
    sprint_dates = SprintDates(
        sprint_tasks.burndown_sheets[sprint_name].index[0],
        len(sprint_tasks.burndown_sheets[sprint_name].index),
        days_off,
    )

    plot_sprint_burn_and_creep(burn_df, sprint_dates, charts_dir, sprint_name)

    sprint_categories_df = burn_categories_df.loc[
        burn_categories_df.index == sprint_name, :
    ].T
    plot_sprint_categories(sprint_categories_df, charts_dir, sprint_name)

    sprint_creep_df = creep_categories_df.loc[
        creep_categories_df.index == sprint_name, :
    ].T
    plot_sprint_creep_categories(sprint_creep_df, charts_dir, sprint_name)


if __name__ == "__main__":
    main()
