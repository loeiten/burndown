"""Module containing the SprintDates class."""

from typing import List, Optional

import pandas as pd
from pandas import Timestamp


class SprintDates:
    """Class which deals with the sprint dates."""

    def __init__(
        self,
        start_date: Timestamp,
        sprint_length: int,
        days_off: Optional[List[Timestamp]] = None,
    ):
        """Set the dates, dates without development and days of development.

        Args:
            start_date (Timestamp): Start date of the sprint
            sprint_length (int): Length of the spring
            days_off (Optional[List[Timestamp]], optional):
                List of days where there will be no sprint. Defaults to None.
        """
        self.dates = None
        self.dates_without_development = None
        self.days_of_development = None

        self.set_dates(start_date, sprint_length)
        self.set_dates_witout_development(days_off)
        self.set_days_of_development(sprint_length)

    def set_dates(self, start_date: Timestamp, sprint_length: int) -> None:
        """Set the dates for the sprint.

        Args:
            start_date (Timestamp): Start date of the sprint
            sprint_length (int): Length of the spring
        """
        self.dates = [
            (start_date + pd.DateOffset(i)).date() for i in range(sprint_length)
        ]

    def set_dates_witout_development(self, days_off: Optional[List[Timestamp]]) -> None:
        """Set the dates where no development is planned.

        Args:
            days_off (Optional[List[Timestamp]], optional):
                List of days where there will be no sprint. Defaults to None.
        """
        # 6 and 7 are iso Saturday and Sunday
        self.dates_witout_development = [
            date for date in self.dates if date.isoweekday() in [6, 7]
        ]
        if days_off is not None:
            self.dates_witout_development += days_off

    def set_days_of_development(self, sprint_length: int) -> None:
        """Set the number of days where there will be development.

        Args:
            sprint_length (int): Length of the spring
        """
        self.days_of_development = sprint_length - len(self.dates_witout_development)
