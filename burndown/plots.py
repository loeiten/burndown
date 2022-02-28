"""Module containing plots."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

from burndown.sprint_dates import SprintDates


def plot_burndown(
    burndown_df: pd.DataFrame,
    sprint_dates: SprintDates,
    save_dir: Path,
    sprint_name: str,
) -> None:
    """Plot and save the burndown.

    Args:
        burndown_df (pd.DataFrame): The data frame containing the burn down
        sprint_dates (SprintDates): Sprint dates object
        save_dir (Path): Directory to store the plot to
        sprint_name (str): Name of the sprint
    """
    plt.style.use("ggplot")
    _, axis = plt.subplots()

    # Shading
    for date in sprint_dates.dates_witout_development:
        xmin = date - pd.DateOffset(1)
        xmax = date
        axis.axvspan(xmin=xmin, xmax=xmax, alpha=0.3, color="gray")

    # Line plots
    (ideal,) = axis.plot(
        burndown_df.index,
        burndown_df["ideal_burndown"],
        linestyle="dashed",
        label="Ideal",
    )
    (remaining,) = axis.plot(
        burndown_df.index,
        burndown_df["remaining"],
        marker=".",
        markersize=9,
        label="Real",
    )

    # Prettifying
    axis.legend(handles=[ideal, remaining], loc="best", shadow=True)
    axis.set_title(f"{sprint_name} burndown")
    axis.set_ylabel("Storypoints")
    axis.set_xlabel("Date")
    axis.set_xticks(burndown_df.index)
    for label in axis.get_xticklabels():
        label.set_rotation(65)

    # Save
    plt.tight_layout()
    save_path = save_dir.joinpath(
        f"{pd.to_datetime('today').date()}-burndown-{sprint_name.lower()}.png"
    )
    print(f"Saving image to: {save_path}")
    plt.savefig(str(save_path), dpi=300, transparent=False)


def plot_sprint_creep(
    sprint_creep_df: pd.DataFrame,
    sprint_dates: SprintDates,
    save_dir: Path,
    sprint_name: str,
) -> None:
    """Plot and save the burn down and creep.

    Args:
        sprint_creep_df (pd.DataFrame): The data frame containing the creep
        sprint_dates (SprintDates): Sprint dates object
        save_dir (Path): Directory to store the plot to
        sprint_name (str): Name of the sprint
    """
    plt.style.use("ggplot")
    _, axis = plt.subplots()

    # Shading
    for date in sprint_dates.dates_witout_development:
        xmin = date - pd.DateOffset(1)
        xmax = date
        axis.axvspan(xmin=xmin, xmax=xmax, alpha=0.3, color="gray")

    # Line plots
    (total,) = axis.plot(
        sprint_creep_df.index,
        sprint_creep_df["accum_burned"],
        marker=".",
        markersize=9,
        label="Total burnt points",
    )
    (creep,) = axis.plot(
        sprint_creep_df.index,
        sprint_creep_df["accum_creep"],
        marker="X",
        markersize=9,
        label="Accumulated creep",
    )

    # Prettifying
    axis.legend(handles=[total, creep], loc="best", shadow=True)
    axis.set_title(f"{sprint_name} Burn and Creep")
    axis.set_ylabel("Storypoints")
    axis.set_xlabel("Date")
    axis.set_xticks(sprint_creep_df.index)
    for label in axis.get_xticklabels():
        label.set_rotation(65)

    # Save
    plt.tight_layout()
    save_path = save_dir.joinpath(
        f"{pd.to_datetime('today').date()}-total_burn_and_creep-{sprint_name.lower()}.png"
    )
    print(f"Saving image to: {save_path}")
    plt.savefig(str(save_path), dpi=300, transparent=False)


def plot_sprint_creep_categories(
    sprint_creep_categories_df: pd.DataFrame, save_dir: Path, sprint_name: str
) -> None:
    """Plot and save the creep categories.

    Args:
        sprint_creep_categories_df (pd.DataFrame): The data frame containing the creep
            categories
        save_dir (Path): Directory to store the plot to
        sprint_name (str): Name of the sprint
    """
    plt.style.use("ggplot")
    _, axis = plt.subplots()

    # Bar plots
    for category, creep in sprint_creep_categories_df.iterrows():
        axis.bar(category, creep, width=0.75)

    # Prettifying
    axis.set_title(f"{sprint_name} Creep Categories")
    axis.set_ylabel("Storypoints")
    axis.set_xlabel("Category")
    for label in axis.get_xticklabels():
        label.set_rotation(90)

    # Save
    plt.tight_layout()
    save_path = save_dir.joinpath(
        f"{pd.to_datetime('today').date()}-creep_categories-{sprint_name.lower()}.png"
    )
    print(f"Saving image to: {save_path}")
    plt.savefig(str(save_path), dpi=300, transparent=False)


def plot_sprint_categories(
    sprint_categories_df: pd.DataFrame, save_dir: Path, sprint_name: str
) -> None:
    """Plot and save the categories.

    Args:
        sprint_categories_df (pd.DataFrame): The data frame containing the
            categories
        save_dir (Path): Directory to store the plot to
        sprint_name (str): Name of the sprint
    """
    plt.style.use("ggplot")
    _, axis = plt.subplots()

    _, axis = plt.subplots()
    for category, creep in sprint_categories_df.iterrows():
        axis.bar(category, creep, width=0.75)

    # Prettifying
    axis.set_title(f"{sprint_name} Categories")
    axis.set_ylabel("Storypoints")
    axis.set_xlabel("Category")
    for label in axis.get_xticklabels():
        label.set_rotation(90)

    # Save
    plt.tight_layout()
    save_path = save_dir.joinpath(
        f"{pd.to_datetime('today').date()}-categories-{sprint_name.lower()}.png"
    )
    print(f"Saving image to: {save_path}")
    plt.savefig(str(save_path), dpi=300, transparent=False)


def plot_burn_trend(burn_trend_df: pd.DataFrame, save_dir: Path) -> None:
    """
    Plot and save the trend of burn categories.

    Args:
        creep_trend_df (pd.DataFrame): The data frame containing the creep trend
        save_dir (Path): Directory to store the plot to
    """
    plt.style.use("ggplot")
    fig, axis = plt.subplots()
    fig.set_size_inches([10, 4.8])

    # Stack plot
    axis.stackplot(
        burn_trend_df.index,
        burn_trend_df.values.T,
        labels=burn_trend_df.columns,
        alpha=0.6,
    )

    # Prettifying
    axis.legend(
        loc="upper left", shadow=True, bbox_to_anchor=(1.04, 1), borderaxespad=0
    )

    axis.set_title("Burned category trend")
    axis.set_ylabel("Storypoints")
    axis.set_xlabel("Sprint")
    for label in axis.get_xticklabels():
        label.set_rotation(65)

    # Save
    plt.tight_layout()
    save_path = save_dir.joinpath(
        f"{pd.to_datetime('today').date()}-category_trend.png"
    )
    print(f"Saving image to: {save_path}")
    plt.savefig(str(save_path), dpi=300, transparent=False)


def plot_creep_trend(creep_trend_df: pd.DataFrame, save_dir: Path) -> None:
    """
    Plot and save the trend of creep categories.

    Args:
        creep_trend_df (pd.DataFrame): The data frame containing the creep trend
        save_dir (Path): Directory to store the plot to
    """
    plt.style.use("ggplot")
    fig, axis = plt.subplots()
    fig.set_size_inches([10, 4.8])

    # Stack plot
    axis.stackplot(
        creep_trend_df.index,
        creep_trend_df.values.T,
        labels=creep_trend_df.columns,
        alpha=0.6,
    )

    # Prettifying
    axis.legend(
        loc="upper left", shadow=True, bbox_to_anchor=(1.04, 1), borderaxespad=0
    )

    axis.set_title("Creep Trend")
    axis.set_ylabel("Storypoints")
    axis.set_xlabel("Sprint")
    for label in axis.get_xticklabels():
        label.set_rotation(65)

    # Save
    plt.tight_layout()
    save_path = save_dir.joinpath(f"{pd.to_datetime('today').date()}-creep_trend.png")
    print(f"Saving image to: {save_path}")
    plt.savefig(str(save_path), dpi=300, transparent=False)


def plot_burndown_trend(burndown_trend_df: pd.DataFrame, save_dir: Path) -> None:
    """
    Plot and save the burndown trend.

    Args:
        burndown_trend_df (pd.DataFrame): The data frame containing the burndowns across
            sprints
        save_dir (Path): Directory to store the plot to
    """
    plt.style.use("ggplot")
    _, axis = plt.subplots()

    # Line plots
    (total,) = axis.plot(
        burndown_trend_df.index,
        burndown_trend_df["total_points"],
        marker=".",
        markersize=9,
        label="Total burnt points",
    )
    (sprint_burn,) = axis.plot(
        burndown_trend_df.index,
        burndown_trend_df["sprint_start_burned"],
        marker="X",
        markersize=9,
        label="Points from sprint planning burned",
    )

    # Prettifying
    axis.legend(handles=[total, sprint_burn], loc="best", shadow=True)

    # Prettifying
    axis.set_title("Burndown Trend")
    axis.set_ylabel("Storypoints")
    axis.set_xlabel("Sprint")
    for label in axis.get_xticklabels():
        label.set_rotation(65)

    # Save
    plt.tight_layout()
    save_path = save_dir.joinpath(
        f"{pd.to_datetime('today').date()}-burndown_trend.png"
    )
    print(f"Saving image to: {save_path}")
    plt.savefig(str(save_path), dpi=300, transparent=False)


def plot_achievement_trend(achievement_df: pd.DataFrame, save_dir: Path) -> None:
    """
    Plot and save the achievement trend.

    Args:
        achievement_df (pd.DataFrame): The data frame containing the burndowns across sprints
        save_dir (Path): Directory to store the plot to
    """
    plt.style.use("ggplot")
    _, axis = plt.subplots()

    # Line plots
    axis.plot(
        achievement_df.index,
        achievement_df["achievement"],
        marker=".",
        markersize=9,
    )

    # Prettifying
    axis.set_title("Points from sprint planning burned")
    axis.set_xlabel("Sprint")
    axis.yaxis.set_major_formatter(mtick.PercentFormatter())
    for label in axis.get_xticklabels():
        label.set_rotation(65)

    # Save
    plt.tight_layout()
    save_path = save_dir.joinpath(
        f"{pd.to_datetime('today').date()}-achievement_trend.png"
    )
    print(f"Saving image to: {save_path}")
    plt.savefig(str(save_path), dpi=300, transparent=False)
