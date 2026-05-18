"""Tests for commit_hour_distribution and hour_distribution_integration."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_hour_distribution import (
    build_hour_distribution,
    format_hour_distribution,
)
from gitlog_digest.hour_distribution_integration import (
    combined_distribution,
    distributions_per_repo,
    hour_distribution_report_dict,
)


def _c(hour: int, author: str = "alice") -> GitCommit:
    dt = datetime(2024, 3, 11, hour, 0, 0, tzinfo=timezone.utc)
    return GitCommit(sha="abc1234", author=author, date=dt, subject="chore: work")


def test_empty_commits_returns_empty_report():
    report = build_hour_distribution([])
    assert report.total == 0
    assert report.peak_hour is None
    assert len(report) == 0


def test_single_commit_counted_correctly():
    report = build_hour_distribution([_c(9)])
    assert report.total == 1
    assert report.peak_hour == 9
    assert report.count_for(9) == 1
    assert report.count_for(10) == 0


def test_multiple_commits_same_hour():
    commits = [_c(14), _c(14), _c(14)]
    report = build_hour_distribution(commits)
    assert report.count_for(14) == 3
    assert report.peak_hour == 14


def test_commits_across_hours():
    commits = [_c(8), _c(8), _c(12), _c(17)]
    report = build_hour_distribution(commits)
    assert report.total == 4
    assert report.peak_hour == 8
    assert report.count_for(12) == 1
    assert report.count_for(17) == 1


def test_sorted_buckets_are_in_order():
    commits = [_c(23), _c(0), _c(12)]
    report = build_hour_distribution(commits)
    hours = [b.hour for b in report.sorted_buckets()]
    assert hours == sorted(hours)


def test_format_contains_peak_hour():
    report = build_hour_distribution([_c(10), _c(10)])
    text = format_hour_distribution(report)
    assert "10:00" in text
    assert "Peak hour" in text


def test_format_empty_report():
    report = build_hour_distribution([])
    text = format_hour_distribution(report)
    assert "No commits" in text


def test_distributions_per_repo_keys():
    data = {"repo-a": [_c(9)], "repo-b": [_c(15), _c(15)]}
    result = distributions_per_repo(data)
    assert set(result.keys()) == {"repo-a", "repo-b"}
    assert result["repo-a"].peak_hour == 9
    assert result["repo-b"].peak_hour == 15


def test_combined_distribution_merges_all():
    data = {"repo-a": [_c(9), _c(9)], "repo-b": [_c(9)]}
    combined = combined_distribution(data)
    assert combined.count_for(9) == 3


def test_report_dict_structure():
    data = {"my-repo": [_c(7), _c(7), _c(22)]}
    d = hour_distribution_report_dict(data)
    assert "peak_hour" in d
    assert "total_commits" in d
    assert "by_hour" in d
    assert len(d["by_hour"]) == 24
    assert d["by_hour"]["07"] == 2
    assert d["total_commits"] == 3
    assert d["repos"]["my-repo"]["peak_hour"] == 7
