"""Test the burndown chart"""

import numpy as np
import pandas as pd
from pathlib import Path

from burndown.excel_io import read_sheet, save_sheet
from burndown.burndown import get_ideal_burndown
from burndown.sprint_dates import SprintDates
from burndown.plot import plot_burndown


def create_test_data(
    sprint_dates: SprintDates, storypoints_start: int, save_dir: Path
) -> None:
    """Create and save test data.

    Args:
        sprint_dates (SprintDates): Sprint dates object
        storypoints_start (int): How many storypoints as start
        save_dir (Path): Where to store the test_data
    """
    ideal_burndown = get_ideal_burndown(sprint_dates, storypoints_start)

    noise = [int(i) for i in np.random.normal(0, 3, len(sprint_dates.dates))]
    noise[0] = 0  # No noise when we start the sprint

    remaining = np.array(ideal_burndown) + np.abs(np.array(noise))
    remaining[5] = remaining[4]  # Saturday
    remaining[6] = remaining[5]  # Sunday
    remaining[-2] = remaining[-3]  # Sunday
    remaining[-1] = remaining[-2]  # Saturday

    df = pd.DataFrame(
        {
            "date": sprint_dates.dates,
            "ideal_burndown": ideal_burndown,
            "remaining": remaining,
        }
    )
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    save_path = save_dir.joinpath("test.xlsx")
    save_sheet(df, save_path, "test")


def test_burndown(tmp_path: Path) -> None:
    """Test that one can plot burndown charts.

    Args:
        tmp_path (Path): Temporary path to save files to
    """
    sprint_length = 14
    # Based on 2021.08.16 - 2022.01.31
    storypoints_start = np.average([26, 23, 23, 20, 20, 21, 35, 19, 24, 43, 18, 28])
    storypoints_start = int(storypoints_start)

    save_path = tmp_path.joinpath("test")
    save_path.mkdir()

    today = pd.to_datetime("2022-01-31")
    sprint_dates = SprintDates(today, sprint_length)
    create_test_data(sprint_dates, storypoints_start, save_path)
    df = read_sheet(save_path.joinpath("test.xlsx"), "test", "date")
    plot_burndown(df, sprint_dates, save_path, "Test")

    assert len(list(save_path.glob("*.png"))) == 1


if __name__ == "__main__":
    test_burndown()
