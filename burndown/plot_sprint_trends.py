"""Script for plotting sprint trends."""

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
    sprint_tasks_path = sheet_dir.joinpath("sprint_tasks.xlsx")
    burndown_path = sheet_dir.joinpath("burndown.xlsx")

    sprint_tasks = SprintTasks(
        sprint_tasks_path=sprint_tasks_path, burndown_path=burndown_path
    )

    burn_categories = sprint_tasks.get_burn_categories()
    plot_burn_trend(burn_categories, charts_dir)
    creep_categories = sprint_tasks.get_creep_categories()
    plot_creep_trend(creep_categories, charts_dir)
    total_burn = sprint_tasks.get_total_burn()
    plot_achievement_trend(total_burn, charts_dir)


if __name__ == "__main__":
    main()
