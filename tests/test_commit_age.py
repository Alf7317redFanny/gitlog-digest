"""Tests for gitlog_digest.commit_age."""
from datetime import date, datetime, timezone

import pytest

from gitlog_digest.commit_age import (
    AgeBucket,
    CommitAgeReport,
    build_age_report,
    format_age_report,
)
from gitlog_digest.git_reader import GitCommit


def _c(days_ago: int, author: str = "alice") -> GitCommit:
    """Create a GitCommit whose date is *days_ago* days before today."""
    dt = datetime(
        2024, 6, 10 - days_ago, 12, 0, 0, tzinfo=timezone.utc
    )
    return GitCommit(
        sha=f"abc{days_ago:03d}",
        author=author,
        date=dt,
        subject=f"commit from {days_ago}d ago",
    )


REF = date(2024, 6, 10)


def test_empty_commits_returns_empty_report():
    report = build_age_report([], reference_date=REF)
    assert report.total == 0
    assert report.buckets == {}


def test_single_commit_placed_in_correct_bucket():
    report = build_age_report([_c(0)], reference_date=REF)
    assert 0 in report.buckets
    assert len(report.buckets[0]) == 1


def test_multiple_commits_same_day_grouped():
    commits = [_c(2), _c(2), _c(2)]
    report = build_age_report(commits, reference_date=REF)
    assert len(report.buckets[2]) == 3
    assert report.total == 3


def test_commits_spread_across_days():
    commits = [_c(0), _c(1), _c(3)]
    report = build_age_report(commits, reference_date=REF)
    assert set(report.buckets.keys()) == {0, 1, 3}
    assert report.total == 3


def test_freshest_day():
    report = build_age_report([_c(0), _c(4)], reference_date=REF)
    assert report.freshest_day == 0


def test_stalest_day():
    report = build_age_report([_c(1), _c(6)], reference_date=REF)
    assert report.stalest_day == 6


def test_freshest_and_stalest_empty():
    report = CommitAgeReport()
    assert report.freshest_day == -1
    assert report.stalest_day == -1


def test_age_bucket_str_today():
    b = AgeBucket(days_ago=0)
    b.commits.append(_c(0))
    assert "today" in str(b)


def test_age_bucket_str_yesterday():
    b = AgeBucket(days_ago=1)
    b.commits.append(_c(1))
    assert "yesterday" in str(b)


def test_age_bucket_str_older():
    b = AgeBucket(days_ago=5)
    b.commits.append(_c(5))
    assert "5d ago" in str(b)


def test_format_age_report_no_commits():
    report = CommitAgeReport()
    text = format_age_report(report)
    assert "No commits" in text


def test_format_age_report_contains_total():
    report = build_age_report([_c(0), _c(2)], reference_date=REF)
    text = format_age_report(report)
    assert "Total: 2" in text


def test_format_age_report_sorted_output():
    report = build_age_report([_c(3), _c(1), _c(0)], reference_date=REF)
    text = format_age_report(report)
    lines = [l for l in text.splitlines() if "ago" in l or "today" in l or "yesterday" in l]
    days = []
    for line in lines:
        if "today" in line:
            days.append(0)
        elif "yesterday" in line:
            days.append(1)
        else:
            days.append(int(line.strip().split("d")[0]))
    assert days == sorted(days)
