from datetime import datetime, timezone

import pytest

from gitlog_digest.commit_longevity import (
    CommitLongevityReport,
    build_longevity_report,
    format_longevity_report,
)
from gitlog_digest.git_reader import GitCommit


def _c(author: str, date_str: str, subject: str = "chore: update") -> GitCommit:
    dt = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    return GitCommit(sha="abc1234", author=author, date=dt, subject=subject, files=[])


def test_empty_commits_returns_empty_report():
    report = build_longevity_report([])
    assert report.total_authors() == 0
    assert report.entries() == []
    assert report.longest_span() is None


def test_single_commit_single_author_span_zero():
    commits = [_c("Alice", "2024-01-10")]
    report = build_longevity_report(commits)
    assert report.total_authors() == 1
    entry = report.longest_span()
    assert entry is not None
    assert entry.span_days == 0
    assert entry.commit_count == 1


def test_two_commits_same_author_span_computed():
    commits = [
        _c("Alice", "2024-01-01"),
        _c("Alice", "2024-01-11"),
    ]
    report = build_longevity_report(commits)
    entry = report.longest_span()
    assert entry.span_days == 10
    assert entry.commit_count == 2


def test_multiple_authors_sorted_by_span():
    commits = [
        _c("Alice", "2024-01-01"),
        _c("Alice", "2024-01-20"),
        _c("Bob", "2024-01-05"),
        _c("Bob", "2024-01-08"),
    ]
    report = build_longevity_report(commits)
    entries = report.entries()
    assert entries[0].author == "Alice"
    assert entries[0].span_days == 19
    assert entries[1].author == "Bob"
    assert entries[1].span_days == 3


def test_first_and_last_dates_tracked_correctly():
    commits = [
        _c("Alice", "2024-03-15"),
        _c("Alice", "2024-01-01"),
        _c("Alice", "2024-06-30"),
    ]
    report = build_longevity_report(commits)
    entry = report.longest_span()
    assert str(entry.first_date) == "2024-01-01"
    assert str(entry.last_date) == "2024-06-30"


def test_top_n_limits_results():
    commits = [
        _c("Alice", "2024-01-01"),
        _c("Alice", "2024-01-30"),
        _c("Bob", "2024-02-01"),
        _c("Bob", "2024-02-05"),
        _c("Carol", "2024-03-01"),
    ]
    report = build_longevity_report(commits)
    assert len(report.top(2)) == 2


def test_top_n_larger_than_entries_returns_all():
    commits = [_c("Alice", "2024-01-01")]
    report = build_longevity_report(commits)
    assert len(report.top(10)) == 1


def test_str_representation():
    commits = [
        _c("Alice", "2024-01-01"),
        _c("Alice", "2024-01-11"),
    ]
    report = build_longevity_report(commits)
    entry = report.longest_span()
    result = str(entry)
    assert "Alice" in result
    assert "10 days" in result


def test_format_longevity_report_empty():
    report = CommitLongevityReport()
    text = format_longevity_report(report)
    assert "No data" in text


def test_format_longevity_report_contains_author():
    commits = [
        _c("Alice", "2024-01-01"),
        _c("Alice", "2024-01-15"),
    ]
    report = build_longevity_report(commits)
    text = format_longevity_report(report)
    assert "Alice" in text
    assert "Commit Longevity" in text
