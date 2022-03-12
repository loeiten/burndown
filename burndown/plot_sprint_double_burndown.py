"""Script for plotting the day to day double burndown (one for sprint burn another for creep burn)."""

import argparse
from pathlib import Path

import pandas as pd

from burndown.plots import plot_achievement_trend, plot_burn_trend, plot_creep_trend
from burndown.sprint_tasks import SprintTasks


def main() -> None:
    """
    Plot the total burn and creep together with the creep categories for a certain sprint.
    """
    parser = argparse.ArgumentParser(description="Plot the sprint trends.")
    parser.add_argument(
        "-r", "--release", type=str, help="Release number", required=True
    )
    parser.add_argument(
        "-u",
        "--until_day",
        type=str,
        help="Until what day to get the burndown to (on the form yyyy-mm-dd)",
    )

    args = parser.parse_args()

    until_day = None if args.until_day is None else pd.to_datetime(args.until_day)

    root_path = Path(__file__).parents[1].resolve()
    charts_dir = root_path.joinpath("charts")
    sheet_dir = root_path.joinpath("data")
    # FIXME: Optional argument date to plot until a specific date
    # FIXME: Update README.md
    sprint_tasks_path = sheet_dir.joinpath("sprint_tasks.xlsx")
    burndown_path = sheet_dir.joinpath("burndown.xlsx")

    sprint_tasks = SprintTasks(
        sprint_tasks_path=sprint_tasks_path, burndown_path=burndown_path
    )

    sprint_planning_burn_df = sprint_tasks.get_sprint_planning_burn(
        sprint_name=args.release
    )
    creep_burn_df = sprint_tasks.get_creep_burn(sprint_name=args.release)

    import pdb

    pdb.set_trace()
    a = 1
    # FIXME: Add a subplot which shows daily creep category as stacked bar plot
    # FIXME: YOU ARE HERE (can use sprint_tasks.sprint_planning_dfs and sprint_tasks.creep_dfs)


if __name__ == "__main__":
    main()
