"""Tests for the week_range module."""

from datetime import datetime, timezone

import pytest

from gitlog_digest.week_range import (
    WeekRange,
    current_week,
    previous_week,
    week_containing,
    weeks_back,
)


def dt(year, month, day, hour=0):
    return datetime(year, month, day, hour, tzinfo=timezone.utc)


def test_week_containing_monday():
    monday = dt(2024, 1, 1)  # known Monday
    wr = week_containing(monday)
    assert wr.start == dt(2024, 1, 1)
    assert wr.end == dt(2024, 1, 7, 23).replace(minute=59, second=59)


def test_week_containing_wednesday():
    wednesday = dt(2024, 1, 3)
    wr = week_containing(wednesday)
    assert wr.start == dt(2024, 1, 1)  # still Monday Jan 1


def test_week_containing_sunday():
    sunday = dt(2024, 1, 7)
    wr = week_containing(sunday)
    assert wr.start == dt(2024, 1, 1)


def test_week_str():
    wr = week_containing(dt(2024, 1, 3))
    assert str(wr) == "2024-01-01 to 2024-01-07"


def test_week_label():
    wr = week_containing(dt(2024, 1, 3))
    assert "January" in wr.label()
    assert "2024" in wr.label()


def test_weeks_back_count():
    result = weeks_back(3)
    assert len(result) == 3
    assert all(isinstance(w, WeekRange) for w in result)


def test_weeks_back_ordering():
    result = weeks_back(3)
    # most recent first
    assert result[0].start > result[1].start > result[2].start


def test_current_week_contains_today():
    wr = current_week()
    now = datetime.now(tz=timezone.utc)
    assert wr.start <= now <= wr.end


def test_previous_week_before_current():
    prev = previous_week()
    curr = current_week()
    assert prev.end < curr.start
