"""
Script for plotting the day to day double burndown (one for sprint burn another for creep burn).
"""

import argparse
from pathlib import Path

import pandas as pd

from burndown.plots import plot_double_burndown
from burndown.sprint_dates import SprintDates
from burndown.sprint_tasks import SprintTasks


def main() -> None:
    """
    Plot the total burn and creep together with the creep categories for a certain sprint.
    """
    parser = argparse.ArgumentParser(description="Plot the sprint trends.")
    parser.add_argument(
        "-r", "--release", type=str, help="Release number", required=True
    )
    parser.add_argument("-s", "--sprint_number", type=str, help="Sprint number")
    parser.add_argument(
        "-u",
        "--until_day",
        type=str,
        help="Until what day to get the burndown to (on the form yyyy-mm-dd)",
    )
    # NOTE: We shouldn't be needing the burndown sheet, and we shouldn't be
    #       needing to add the days off argument every time. This is just due
    #       to tech debt
    parser.add_argument(
        "-d",
        "--days_off",
        nargs="+",
        type=str,
        help="Days without development on the form yyyy-mm-dd (week-ends are inferred)",
    )

    args = parser.parse_args()
    sprint_name = f"{args.release}-{args.sprint_number}"

    until_day = (
        pd.to_datetime("today")
        if args.until_day is None
        else pd.to_datetime(args.until_day)
    )

    root_path = Path(__file__).parents[1].resolve()
    charts_dir = root_path.joinpath("charts")
    sheet_dir = root_path.joinpath("data")
    sprint_tasks_path = sheet_dir.joinpath("sprint_tasks.xlsx")
    burndown_path = sheet_dir.joinpath("burndown.xlsx")

    sprint_tasks = SprintTasks(
        sprint_tasks_path=sprint_tasks_path, burndown_path=burndown_path
    )

    # In case until_day is outside of the sprint range
    if until_day > sprint_tasks.burndown_sheets[sprint_name].index.max():
        until_day = sprint_tasks.burndown_sheets[sprint_name].index.max()

    sprint_planning_burn_df = sprint_tasks.get_sprint_planning_burn(
        sprint_name=sprint_name, until_date=until_day
    )
    sprint_planning_burn_df = pd.concat(
        [
            sprint_planning_burn_df,
            sprint_tasks.burndown_sheets[sprint_name].loc[:, ["ideal_burndown"]],
        ],
        axis=1,
    )
    creep_burn_df = sprint_tasks.get_creep_burn(
        sprint_name=sprint_name, until_date=until_day
    )
    daily_creep = sprint_tasks.get_daily_creep(
        sprint_name=sprint_name, until_date=until_day
    )

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

    plot_double_burndown(
        sprint_burndown_df=sprint_planning_burn_df,
        creep_burndown_df=creep_burn_df,
        daily_creep=daily_creep,
        sprint_dates=sprint_dates,
        save_dir=charts_dir,
        sprint_name=sprint_name,
    )


if __name__ == "__main__":
    main()
