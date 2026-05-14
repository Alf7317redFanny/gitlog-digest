"""Utilities for computing weekly date ranges."""

from datetime import datetime, timedelta, timezone
from dataclasses import dataclass


@dataclass(frozen=True)
class WeekRange:
    start: datetime  # Monday 00:00:00 UTC
    end: datetime    # Sunday 23:59:59 UTC

    def __str__(self) -> str:
        return f"{self.start.strftime('%Y-%m-%d')} to {self.end.strftime('%Y-%m-%d')}"

    def label(self) -> str:
        return f"Week of {self.start.strftime('%B %d, %Y')}"


def current_week() -> WeekRange:
    """Return the WeekRange for the current calendar week (Mon–Sun, UTC)."""
    now = datetime.now(tz=timezone.utc)
    return week_containing(now)


def previous_week() -> WeekRange:
    """Return the WeekRange for last calendar week."""
    now = datetime.now(tz=timezone.utc)
    last_week_day = now - timedelta(weeks=1)
    return week_containing(last_week_day)


def week_containing(dt: datetime) -> WeekRange:
    """Return the WeekRange (Mon–Sun) that contains the given datetime."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    monday = dt - timedelta(days=dt.weekday())
    start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return WeekRange(start=start, end=end)


def weeks_back(n: int) -> list[WeekRange]:
    """Return a list of the last n completed week ranges, most recent first."""
    now = datetime.now(tz=timezone.utc)
    ranges = []
    for i in range(1, n + 1):
        target = now - timedelta(weeks=i)
        ranges.append(week_containing(target))
    return ranges
