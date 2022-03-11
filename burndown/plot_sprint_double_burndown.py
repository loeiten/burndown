"""Script for plotting the day to day double burndown (one for sprint burn another for creep burn)."""

import argparse
from pathlib import Path

from burndown.plots import plot_achievement_trend, plot_burn_trend, plot_creep_trend
from burndown.sprint_tasks import SprintTasks


def main() -> None:
    """
    Plot the total burn and creep together with the creep categories for a certain sprint.
    """
    argparse.ArgumentParser(description="Plot the sprint trends.")

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
    # FIXME: YOU ARE HERE (can use sprint_tasks.sprint_planning_dfs and sprint_tasks.creep_dfs)


if __name__ == "__main__":
    main()
