"""Tests for author_velocity and velocity_integration."""
from datetime import datetime

import pytest

from gitlog_digest.author_velocity import (
    AuthorVelocityEntry,
    compute_velocity,
    format_velocity_report,
)
from gitlog_digest.velocity_integration import (
    combined_velocity,
    format_all_velocity_reports,
    velocity_per_repo,
    velocity_report_dict,
)


def _c(author: str, dt: str, sha: str = "abc1234"):
    from gitlog_digest.git_reader import GitCommit
    return GitCommit(
        sha=sha,
        author=author,
        date=datetime.fromisoformat(dt),
        message="some commit",
    )


def test_empty_commits_returns_empty_report():
    report = compute_velocity([])
    assert len(report) == 0
    assert report.top() == []


def test_single_commit_velocity_is_one():
    commits = [_c("Alice", "2024-03-04T10:00:00")]
    report = compute_velocity(commits)
    assert len(report) == 1
    entry = report.entries[0]
    assert entry.author == "Alice"
    assert entry.total_commits == 1
    assert entry.active_days == 1
    assert entry.velocity == 1.0


def test_two_commits_same_day_velocity_is_two():
    commits = [
        _c("Bob", "2024-03-04T09:00:00"),
        _c("Bob", "2024-03-04T17:00:00"),
    ]
    report = compute_velocity(commits)
    assert report.entries[0].velocity == 2.0
    assert report.entries[0].active_days == 1


def test_commits_across_days_averages_correctly():
    commits = [
        _c("Carol", "2024-03-04T10:00:00"),
        _c("Carol", "2024-03-05T10:00:00"),
        _c("Carol", "2024-03-06T10:00:00"),
        _c("Carol", "2024-03-06T15:00:00"),
    ]
    report = compute_velocity(commits)
    entry = report.entries[0]
    assert entry.total_commits == 4
    assert entry.active_days == 3
    assert entry.velocity == round(4 / 3, 2)


def test_multiple_authors_sorted_by_velocity():
    commits = [
        _c("Slow", "2024-03-04T10:00:00"),
        _c("Slow", "2024-03-05T10:00:00"),
        _c("Fast", "2024-03-04T10:00:00"),
        _c("Fast", "2024-03-04T12:00:00"),
        _c("Fast", "2024-03-04T14:00:00"),
    ]
    report = compute_velocity(commits)
    assert report.entries[0].author == "Fast"
    assert report.entries[1].author == "Slow"


def test_velocity_entry_str():
    entry = AuthorVelocityEntry(author="Dev", total_commits=6, active_days=3)
    assert "Dev" in str(entry)
    assert "2.00" in str(entry)


def test_format_velocity_report_empty():
    from gitlog_digest.author_velocity import AuthorVelocityReport
    text = format_velocity_report(AuthorVelocityReport())
    assert "no data" in text


def test_format_velocity_report_contains_author():
    commits = [_c("Alice", "2024-03-04T10:00:00")]
    report = compute_velocity(commits)
    text = format_velocity_report(report)
    assert "Alice" in text


def test_velocity_per_repo_keys():
    repo_commits = {
        "repo-a": [_c("Alice", "2024-03-04T10:00:00")],
        "repo-b": [_c("Bob", "2024-03-05T10:00:00")],
    }
    per_repo = velocity_per_repo(repo_commits)
    assert set(per_repo.keys()) == {"repo-a", "repo-b"}


def test_combined_velocity_merges_all():
    repo_commits = {
        "repo-a": [_c("Alice", "2024-03-04T10:00:00")],
        "repo-b": [_c("Alice", "2024-03-05T10:00:00")],
    }
    combined = combined_velocity(repo_commits)
    assert combined.entries[0].total_commits == 2
    assert combined.entries[0].active_days == 2


def test_velocity_report_dict_structure():
    repo_commits = {
        "repo-a": [_c("Alice", "2024-03-04T10:00:00")],
    }
    d = velocity_report_dict(repo_commits)
    assert "per_repo" in d
    assert "combined" in d
    assert "repo-a" in d["per_repo"]
    assert d["per_repo"]["repo-a"][0]["author"] == "Alice"


def test_format_all_velocity_reports_contains_repo_name():
    repo_commits = {
        "my-repo": [_c("Dev", "2024-03-04T10:00:00")],
    }
    text = format_all_velocity_reports(repo_commits)
    assert "my-repo" in text
    assert "combined" in text
