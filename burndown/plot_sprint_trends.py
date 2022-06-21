"""Script for plotting sprint trends."""

import argparse
from pathlib import Path

from burndown.plots import (
    plot_achievement_trend,
    plot_burn_per_person_day,
    plot_burn_trend,
    plot_creep_trend,
)
from burndown.sprint_tasks import SprintTasks


def main() -> None:
    """
    Plot the total burn and creep together with the creep categories for a certain sprint.
    """
    parser = argparse.ArgumentParser(description="Plot the sprint trends.")
    parser.add_argument(
        "-r",
        "--release",
        type=str,
        help="Release number (if none is given, the trends will be plotted over all releases)",
    )
    args = parser.parse_args()

    root_path = Path(__file__).parents[1].resolve()
    charts_dir = root_path.joinpath("charts")
    sheet_dir = root_path.joinpath("data")
    sprint_tasks_path = sheet_dir.joinpath("sprint_tasks.xlsx")
    burndown_path = sheet_dir.joinpath("burndown.xlsx")

    sprint_tasks = SprintTasks(
        sprint_tasks_path=sprint_tasks_path, burndown_path=burndown_path
    )

    # Obtain the data frames
    total_burn = sprint_tasks.get_total_burn()
    burn_categories = sprint_tasks.get_burn_categories()
    creep_categories = sprint_tasks.get_creep_categories()

    # Print release statistics
    burn_categories_sum = burn_categories.groupby("Release").sum()
    creep_categories_sum = creep_categories.groupby("Release").sum()
    person_day_sum = (
        total_burn.loc[:, ["person_days", "Release"]].groupby("Release").sum()
    )
    print("Absolute sum:")
    print("=" * 80)
    print("Total person days:")
    print("-" * 80)
    print(person_day_sum.sum(axis=1))
    print("-" * 80)
    print("Total points burned:")
    print("-" * 80)
    print(burn_categories_sum.sum(axis=1))
    print("-" * 80)
    print("Total points creep:")
    print("-" * 80)
    print(creep_categories_sum.sum(axis=1))
    print("-" * 80)
    print("\n")
    print("Points burned:")
    print("=" * 80)
    print("Points burned per category:")
    print("-" * 80)
    print(burn_categories_sum)
    print("-" * 80)
    print("Creep burned per category:")
    print("-" * 80)
    print(creep_categories_sum)
    print("-" * 80)
    print("\n")
    print("Percentage burned:")
    print("=" * 80)
    print("Percentage burned per category:")
    print("-" * 80)
    print(100 * burn_categories_sum.div(burn_categories_sum.sum(axis=1), axis=0))
    print("-" * 80)
    print("Percentage creep per category:")
    print("-" * 80)
    print(100 * creep_categories_sum.div(creep_categories_sum.sum(axis=1), axis=0))
    print("-" * 80)
    print("\n")

    # Get the required release and drop the column
    if args.release is not None:
        total_burn = total_burn.loc[total_burn.loc[:, "Release"] == args.release, :]
        burn_categories = burn_categories.loc[
            burn_categories.loc[:, "Release"] == args.release, :
        ]
        creep_categories = creep_categories.loc[
            total_burn.loc[:, "Release"] == args.release, :
        ]
    total_burn.drop("Release", axis=1, inplace=True)
    burn_categories.drop("Release", axis=1, inplace=True)
    creep_categories.drop("Release", axis=1, inplace=True)

    # Make percentage data frames
    burn_categories_row_pct = 100 * burn_categories.div(
        burn_categories.sum(axis=1), axis=0
    )
    # We must remove negative numbers from re-estimation
    creep_categories_row_pct = creep_categories.clip(lower=0)
    creep_categories_row_pct = 100 * creep_categories_row_pct.div(
        creep_categories_row_pct.sum(axis=1), axis=0
    )

    # Plot
    plot_burn_trend(burn_categories, charts_dir, percentage=False)
    plot_burn_trend(burn_categories_row_pct, charts_dir, percentage=True)
    plot_creep_trend(creep_categories, charts_dir, percentage=False)
    plot_creep_trend(creep_categories_row_pct, charts_dir, percentage=True)
    plot_achievement_trend(total_burn, charts_dir)
    plot_burn_per_person_day(total_burn, charts_dir)


if __name__ == "__main__":
    main()
