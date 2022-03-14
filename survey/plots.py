"""Module containing survey plots."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_agile_maturity(
    agile_maturity_df: pd.DataFrame,
    save_dir: Path,
) -> None:
    """Plot and save the agile maturity.

    Modified from
    https://python-graph-gallery.com/391-radar-chart-with-several-individuals

    Args:
        agile_maturity_df (pd.DataFrame): The data frame containing the results of the agile
            maturity
        save_dir (Path): Directory to store the plot to
    """
    plt.style.use("ggplot")
    _, axis = plt.subplots(subplot_kw={"projection": "polar"})

    # Get the number of dimensions
    dimensions = list(agile_maturity_df.columns)
    n_dim = len(dimensions)

    # Calculate the angles for each axis in the plot
    angles = [n / float(n_dim) * 2 * np.pi for n in range(n_dim)]
    # We add an additional angle for the polygon to close
    angles.append(angles[0])

    for sprint_name, value_series in agile_maturity_df.iterrows():
        values = list(value_series.values)
        # We add an additional value for the polygon to close
        values.append(values[0])
        axis.plot(angles, values, linewidth=1, linestyle="solid", label=sprint_name)
        axis.fill(angles, values, alpha=0.1)

    # Prettifying
    axis.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))
    axis.set_rlabel_position(0)
    # Set y-ticks (maximum score is 5)
    axis.set_yticks(list(range(6)))
    # Draw one axis per variable
    axis.set_xticks(angles[:-1])
    axis.set_xticklabels(dimensions)
    # Set title
    axis.set_title("Agile maturity assessment")

    # Save
    plt.tight_layout()
    save_path = save_dir.joinpath(
        f"{pd.to_datetime('today').date()}-agile_assessment.png"
    )
    print(f"Saving image to: {save_path}")
    plt.savefig(str(save_path), dpi=300, transparent=False)
