"""Edge-case tests for commit_burst.py"""
from datetime import date, datetime, timezone
from types import SimpleNamespace

import pytest

from gitlog_digest.commit_burst import build_burst_report, _BURST_MULTIPLIER


def _c(day: str, hour: int = 9):
    dt = datetime.fromisoformat(f"{day}T{hour:02d}:00:00").replace(
        tzinfo=timezone.utc
    )
    return SimpleNamespace(date=dt, sha="sha", author="a", subject="s", files=[])


def test_custom_multiplier_lower_threshold_finds_more_bursts():
    commits = [_c("2024-02-01")] * 2 + [_c("2024-02-02")] * 4
    # with multiplier=1.2, both days might qualify
    report = build_burst_report(commits, multiplier=1.2)
    assert report.total_burst_days >= 1


def test_custom_multiplier_very_high_finds_no_bursts():
    commits = [_c("2024-02-01")] * 2 + [_c("2024-02-02")] * 4
    report = build_burst_report(commits, multiplier=100.0)
    assert report.total_burst_days == 0


def test_exactly_at_threshold_counts_as_burst():
    # 1 commit on day A, 1 on day B, 4 on day C → avg = 2.0; 4 == 2.0 * 2.0
    commits = [_c("2024-03-01")] + [_c("2024-03-02")] + [_c("2024-03-03")] * 4
    report = build_burst_report(commits)
    assert report.total_burst_days == 1
    assert report.peak.count == 4


def test_just_below_threshold_not_burst():
    # avg = 2.0, need >= 4 to burst; day C has 3
    commits = [_c("2024-03-01")] + [_c("2024-03-02")] + [_c("2024-03-03")] * 3
    report = build_burst_report(commits)
    assert report.total_burst_days == 0


def test_all_commits_same_day_no_burst():
    commits = [_c("2024-04-10")] * 100
    report = build_burst_report(commits)
    # only one day: ratio == 1.0, below multiplier
    assert report.total_burst_days == 0
    assert report.average_daily == 100.0


def test_two_days_equal_counts_no_burst():
    commits = [_c("2024-05-01")] * 5 + [_c("2024-05-02")] * 5
    report = build_burst_report(commits)
    # ratio == 1.0 for both days
    assert report.total_burst_days == 0
