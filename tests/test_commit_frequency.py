"""Tests for gitlog_digest.commit_frequency."""
from datetime import datetime, timezone

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_frequency import (
    build_frequency,
    format_frequency_report,
    CommitFrequency,
    FrequencyBucket,
)


def _c(iso: str, author: str = "alice") -> GitCommit:
    dt = datetime.fromisoformat(iso).replace(tzinfo=timezone.utc)
    return GitCommit(sha="abc1234", author=author, date=dt, message="msg")


def test_empty_commits_returns_empty_frequency():
    freq = build_frequency([])
    assert freq.total == 0
    assert freq.buckets == []
    assert freq.peak is None
    assert freq.average == 0.0
    assert freq.days_with_commits() == 0


def test_single_commit_single_bucket():
    freq = build_frequency([_c("2024-03-04T10:00:00")])
    assert len(freq.buckets) == 1
    assert freq.total == 1
    assert freq.days_with_commits() == 1


def test_multiple_commits_same_day_grouped():
    commits = [
        _c("2024-03-04T09:00:00"),
        _c("2024-03-04T14:00:00"),
        _c("2024-03-04T18:30:00"),
    ]
    freq = build_frequency(commits)
    assert len(freq.buckets) == 1
    assert freq.buckets[0].count == 3
    assert freq.total == 3


def test_commits_across_multiple_days():
    commits = [
        _c("2024-03-04T10:00:00"),
        _c("2024-03-05T11:00:00"),
        _c("2024-03-05T15:00:00"),
        _c("2024-03-07T08:00:00"),
    ]
    freq = build_frequency(commits)
    assert len(freq.buckets) == 3
    assert freq.total == 4
    assert freq.days_with_commits() == 3


def test_peak_day_is_highest_count():
    commits = [
        _c("2024-03-04T10:00:00"),
        _c("2024-03-05T11:00:00"),
        _c("2024-03-05T12:00:00"),
    ]
    freq = build_frequency(commits)
    assert freq.peak is not None
    assert freq.peak.count == 2


def test_average_over_active_days_only():
    commits = [
        _c("2024-03-04T10:00:00"),
        _c("2024-03-06T11:00:00"),
        _c("2024-03-06T12:00:00"),
    ]
    freq = build_frequency(commits)
    # 3 commits over 2 active days
    assert freq.average == pytest.approx(1.5)


def test_buckets_sorted_by_date():
    commits = [
        _c("2024-03-07T10:00:00"),
        _c("2024-03-04T10:00:00"),
        _c("2024-03-05T10:00:00"),
    ]
    freq = build_frequency(commits)
    days = [b.day.day for b in freq.buckets]
    assert days == sorted(days)


def test_format_empty_frequency():
    report = format_frequency_report(CommitFrequency(buckets=[]))
    assert "No commits" in report


def test_format_frequency_report_contains_peak():
    commits = [
        _c("2024-03-04T10:00:00"),
        _c("2024-03-04T12:00:00"),
    ]
    report = format_frequency_report(build_frequency(commits))
    assert "Peak day" in report
    assert "2024-03-04" in report


def test_frequency_bucket_str_singular():
    from datetime import date
    b = FrequencyBucket(day=date(2024, 3, 4), count=1)
    assert str(b) == "2024-03-04: 1 commit"


def test_frequency_bucket_str_plural():
    from datetime import date
    b = FrequencyBucket(day=date(2024, 3, 4), count=5)
    assert str(b) == "2024-03-04: 5 commits"
