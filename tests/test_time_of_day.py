"""Tests for gitlog_digest.time_of_day."""

from datetime import datetime, timezone

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.time_of_day import (
    TimeOfDayReport,
    build_time_of_day_report,
    format_time_of_day_report,
)


def _c(hour: int) -> GitCommit:
    dt = datetime(2024, 3, 15, hour, 0, 0, tzinfo=timezone.utc)
    return GitCommit(sha="abc1234", author="Dev", date=dt, message="msg")


def test_empty_commits_returns_zero_counts():
    report = build_time_of_day_report([])
    assert report.total == 0
    assert all(v == 0 for v in report.counts.values())


def test_empty_peak_period_is_none():
    report = TimeOfDayReport()
    assert report.peak_period is None


def test_night_bucket(  ):
    report = build_time_of_day_report([_c(0), _c(3), _c(5)])
    assert report.counts["night"] == 3


def test_morning_bucket():
    report = build_time_of_day_report([_c(6), _c(9), _c(11)])
    assert report.counts["morning"] == 3


def test_afternoon_bucket():
    report = build_time_of_day_report([_c(12), _c(15), _c(17)])
    assert report.counts["afternoon"] == 3


def test_evening_bucket():
    report = build_time_of_day_report([_c(18), _c(21), _c(23)])
    assert report.counts["evening"] == 3


def test_mixed_commits_totals():
    commits = [_c(2), _c(8), _c(14), _c(20)]
    report = build_time_of_day_report(commits)
    assert report.total == 4
    assert report.counts["night"] == 1
    assert report.counts["morning"] == 1
    assert report.counts["afternoon"] == 1
    assert report.counts["evening"] == 1


def test_peak_period_returns_busiest_bucket():
    commits = [_c(9), _c(10), _c(11), _c(14)]
    report = build_time_of_day_report(commits)
    assert report.peak_period == "morning"


def test_len_equals_total():
    commits = [_c(7), _c(8)]
    report = build_time_of_day_report(commits)
    assert len(report) == 2


def test_format_contains_bucket_names():
    commits = [_c(9), _c(14)]
    report = build_time_of_day_report(commits)
    text = format_time_of_day_report(report)
    for name in ("morning", "afternoon", "evening", "night"):
        assert name in text


def test_format_empty_returns_no_commits():
    report = TimeOfDayReport()
    assert format_time_of_day_report(report) == "No commits."


def test_format_contains_peak_label():
    report = build_time_of_day_report([_c(20), _c(21), _c(22)])
    text = format_time_of_day_report(report)
    assert "peak" in text
    assert "evening" in text
