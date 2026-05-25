"""Tests for velocity_trend_integration module."""
from datetime import datetime, timezone

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.velocity_trend_integration import (
    trends_per_repo,
    combined_trend,
    velocity_trend_report_dict,
    format_all_velocity_trend_reports,
)


def _c(author: str) -> GitCommit:
    return GitCommit(
        sha="deadbeef",
        author=author,
        date=datetime(2024, 3, 1, 9, 0, tzinfo=timezone.utc),
        subject="feat: something",
        files_changed=[],
    )


def test_trends_per_repo_keys_match_input():
    data = {
        "repo-a": [[_c("alice")], [_c("alice"), _c("alice")]],
        "repo-b": [[_c("bob")]],
    }
    result = trends_per_repo(data)
    assert set(result.keys()) == {"repo-a", "repo-b"}


def test_trends_per_repo_are_independent():
    data = {
        "repo-a": [[_c("alice")]],
        "repo-b": [[_c("bob")]],
    }
    result = trends_per_repo(data)
    authors_a = {e.author for e in result["repo-a"].entries()}
    authors_b = {e.author for e in result["repo-b"].entries()}
    assert "alice" in authors_a
    assert "bob" not in authors_a
    assert "bob" in authors_b


def test_combined_trend_merges_all_commits():
    data = {
        "repo-a": [[_c("alice"), _c("alice")]],
        "repo-b": [[_c("alice")]],
    }
    report = combined_trend(data)
    alice = next(e for e in report.entries() if e.author == "alice")
    assert alice.weekly_counts == [3]


def test_combined_trend_empty_input():
    report = combined_trend({})
    assert len(report) == 0


def test_combined_trend_different_week_counts():
    data = {
        "repo-a": [[_c("alice")], [_c("alice")]],
        "repo-b": [[_c("bob")]],
    }
    report = combined_trend(data)
    assert len(report) >= 1


def test_velocity_trend_report_dict_structure():
    data = {"repo-a": [[_c("alice"), _c("alice")], [_c("alice")]]}
    report = trends_per_repo(data)["repo-a"]
    d = velocity_trend_report_dict(report)
    assert "top_authors" in d
    assert "total_tracked_authors" in d
    assert d["top_authors"][0]["author"] == "alice"
    assert "trend" in d["top_authors"][0]


def test_format_all_velocity_trend_reports_contains_repo_name():
    data = {"my-repo": [[_c("alice")]]}
    text = format_all_velocity_trend_reports(data)
    assert "my-repo" in text


def test_format_all_velocity_trend_reports_empty():
    text = format_all_velocity_trend_reports({})
    assert text == ""
