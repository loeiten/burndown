import argparse
import pandas as pd
from burndown.sprint_dates import SprintDates
from burndown.excel_io import read_sheet
import matplotlib.pyplot as plt
from pathlib import Path


def plot_burndown(
    df: pd.DataFrame, sprint_dates: SprintDates, save_dir: Path, sprint_name: str
) -> None:
    """Plot and save the burndown.

    Args:
        df (pd.DataFrame): The data frame containing the burn down
        sprint_dates (SprintDates): Sprint dates object
        save_dir (Path): Directory to store the plot to
        sprint_name (str): Name of the sprint
    """
    plt.style.use("ggplot")
    _, ax = plt.subplots()

    # Shading
    for date in sprint_dates.dates_witout_development:
        xmin = date - pd.DateOffset(1)
        xmax = date
        ax.axvspan(xmin=xmin, xmax=xmax, alpha=0.3, color="gray")

    # Line plots
    (ideal,) = ax.plot(
        df.index, df["ideal_burndown"], linestyle="dashed", label="Ideal"
    )
    (remaining,) = ax.plot(
        df.index, df["remaining"], marker=".", markersize=9, label="Real"
    )

    # Prettifying
    ax.legend(handles=[ideal, remaining], loc="best", shadow=True)
    ax.set_title(f"{sprint_name} burndown")
    ax.set_ylabel("Storypoints")
    ax.set_xlabel("Date")
    ax.set_xticks(df.index)
    for label in ax.get_xticklabels():
        label.set_rotation(65)

    # Save
    plt.tight_layout()
    save_path = save_dir.joinpath(
        f"{pd.to_datetime('today').date()}-burndown-{sprint_name.lower()}.png"
    )
    print(f"Saving image to: {save_path}")
    plt.savefig(str(save_path), dpi=300, transparent=False)


def plot_total_burn_and_creep(
    df: pd.DataFrame, sprint_dates: SprintDates, save_dir: Path, sprint_name: str
) -> None:
    """Plot and save the burn down and creep.

    Args:
        df (pd.DataFrame): The data frame containing the creep
        sprint_dates (SprintDates): Sprint dates object
        save_dir (Path): Directory to store the plot to
        sprint_name (str): Name of the sprint
    """
    plt.style.use("ggplot")
    _, ax = plt.subplots()

    # Shading
    for date in sprint_dates.dates_witout_development:
        xmin = date - pd.DateOffset(1)
        xmax = date
        ax.axvspan(xmin=xmin, xmax=xmax, alpha=0.3, color="gray")

    # Line plots
    (total,) = ax.plot(
        df.index,
        df["accum_burned"],
        marker=".",
        markersize=9,
        label="Total burnt points",
    )
    (creep,) = ax.plot(
        df.index, df["accum_creep"], marker="X", markersize=9, label="Accumulated creep"
    )

    # Prettifying
    ax.legend(handles=[total, creep], loc="best", shadow=True)
    ax.set_title(f"{sprint_name} Burn and Creep")
    ax.set_ylabel("Storypoints")
    ax.set_xlabel("Date")
    ax.set_xticks(df.index)
    for label in ax.get_xticklabels():
        label.set_rotation(65)

    # Save
    plt.tight_layout()
    save_path = save_dir.joinpath(
        f"{pd.to_datetime('today').date()}-total_burn_and_creep-{sprint_name.lower()}.png"
    )
    print(f"Saving image to: {save_path}")
    plt.savefig(str(save_path), dpi=300, transparent=False)


def plot_creep_categories(df: pd.DataFrame, save_dir: Path, sprint_name: str) -> None:
    """Plot and save the creep categories.

    Args:
        df (pd.DataFrame): The data frame containing the creep
        save_dir (Path): Directory to store the plot to
        sprint_name (str): Name of the sprint
    """
    plt.style.use("ggplot")
    _, ax = plt.subplots()

    # Bar plots
    for category, creep in df.iterrows():
        ax.bar(category, creep, width=0.75)

    # Prettifying
    ax.set_title(f"{sprint_name} Creep Categories")
    ax.set_ylabel("Storypoints")
    ax.set_xlabel("Category")
    for label in ax.get_xticklabels():
        label.set_rotation(90)

    # Save
    plt.tight_layout()
    save_path = save_dir.joinpath(
        f"{pd.to_datetime('today').date()}-creep_categories-{sprint_name.lower()}.png"
    )
    print(f"Saving image to: {save_path}")
    plt.savefig(str(save_path), dpi=300, transparent=False)


if __name__ == "__main__":
    date = pd.to_datetime("today")
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

    df = read_sheet(sheet_path, sheet_name, index_col="date")
    days_off = (
        [pd.to_datetime(date) for date in args.days_off]
        if args.days_off is not None
        else None
    )
    sprint_dates = SprintDates(df.index[0], len(df.index), days_off)

    plot_burndown(df, sprint_dates, charts_dir, sheet_name)
