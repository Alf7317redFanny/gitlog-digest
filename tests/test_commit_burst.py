"""Tests for commit_burst.py"""
from datetime import datetime, timezone

import pytest

from gitlog_digest.commit_burst import (
    BurstDay,
    CommitBurstReport,
    build_burst_report,
    format_burst_report,
)


def _c(day: str, hour: int = 10) -> object:
    """Minimal GitCommit-like object."""
    from types import SimpleNamespace

    dt = datetime.fromisoformat(f"{day}T{hour:02d}:00:00").replace(
        tzinfo=timezone.utc
    )
    return SimpleNamespace(date=dt, sha="abc1234", author="dev", subject="msg", files=[])


def test_empty_commits_returns_empty_report():
    report = build_burst_report([])
    assert report.total_burst_days == 0
    assert report.peak is None
    assert report.average_daily == 0.0


def test_single_day_no_burst():
    commits = [_c("2024-01-01")] * 3
    report = build_burst_report(commits)
    # only one day — average == count, ratio == 1.0, never >= 2x
    assert report.total_burst_days == 0


def test_burst_detected_when_day_doubles_average():
    # day A: 1 commit, day B: 1 commit, day C: 10 commits → avg = 4, C ratio = 2.5
    commits = [_c("2024-01-01")] + [_c("2024-01-02")] + [_c("2024-01-03")] * 10
    report = build_burst_report(commits)
    assert report.total_burst_days == 1
    assert report.peak is not None
    from datetime import date
    assert report.peak.day == date(2024, 1, 3)
    assert report.peak.count == 10


def test_average_daily_computed_correctly():
    commits = [_c("2024-01-01")] * 2 + [_c("2024-01-02")] * 4
    report = build_burst_report(commits)
    assert report.average_daily == 3.0


def test_burst_ratio_value():
    commits = [_c("2024-01-01")] * 1 + [_c("2024-01-02")] * 1 + [_c("2024-01-03")] * 8
    report = build_burst_report(commits)
    peak = report.peak
    assert peak is not None
    expected_avg = 10 / 3
    expected_ratio = 8 / expected_avg
    assert abs(peak.ratio - expected_ratio) < 0.01


def test_multiple_burst_days_sorted_by_count():
    commits = (
        [_c("2024-01-01")] * 1
        + [_c("2024-01-02")] * 6
        + [_c("2024-01-03")] * 9
    )
    report = build_burst_report(commits)
    counts = [b.count for b in report.bursts]
    assert counts == sorted(counts, reverse=True)


def test_format_burst_report_no_bursts():
    report = CommitBurstReport(average_daily=1.0)
    text = format_burst_report(report)
    assert "(none)" in text


def test_format_burst_report_shows_day():
    from datetime import date
    burst = BurstDay(day=date(2024, 3, 15), count=12, ratio=3.0)
    report = CommitBurstReport(_bursts=[burst], average_daily=4.0)
    text = format_burst_report(report)
    assert "2024-03-15" in text
    assert "12" in text


def test_burst_day_str():
    from datetime import date
    b = BurstDay(day=date(2024, 6, 1), count=7, ratio=2.5)
    assert "2024-06-01" in str(b)
    assert "7" in str(b)
    assert "2.5x" in str(b)
