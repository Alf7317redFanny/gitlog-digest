"""Tests for commit_flow and flow_integration modules."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_flow import (
    _classify_flow,
    build_flow_report,
    format_flow_report,
)
from gitlog_digest.flow_integration import (
    combined_flow,
    flow_per_repo,
    flow_report_dict,
)


def _c(subject: str, day: str = "2024-03-11", author: str = "alice") -> GitCommit:
    dt = datetime.fromisoformat(f"{day}T10:00:00").replace(tzinfo=timezone.utc)
    return GitCommit(sha="abc1234", subject=subject, author=author, date=dt, files=[])


# --- _classify_flow ---

def test_classify_flow_feat():
    assert _classify_flow("feat: add login page") == "add"


def test_classify_flow_fix():
    assert _classify_flow("fix: resolve null pointer") == "fix"


def test_classify_flow_refactor():
    assert _classify_flow("refactor auth module") == "refactor"


def test_classify_flow_remove():
    assert _classify_flow("remove deprecated endpoint") == "remove"


def test_classify_flow_unknown_returns_other():
    assert _classify_flow("bump version to 2.0") == "other"


def test_classify_flow_case_insensitive():
    assert _classify_flow("FIX: crash on startup") == "fix"


# --- CommitFlowReport ---

def test_empty_commits_returns_empty_report():
    report = build_flow_report([])
    assert report.total == 0
    assert report.entries() == []
    assert report.dominant_type() is None


def test_single_commit_counted_correctly():
    report = build_flow_report([_c("add new feature")])
    assert report.total == 1
    assert len(report.entries()) == 1
    assert report.entries()[0].add == 1


def test_multiple_commits_same_day_grouped():
    commits = [_c("feat: x"), _c("fix: y"), _c("add z")]
    report = build_flow_report(commits)
    assert len(report.entries()) == 1
    entry = report.entries()[0]
    assert entry.total == 3


def test_commits_across_days_sorted():
    commits = [_c("fix a", "2024-03-13"), _c("add b", "2024-03-11")]
    report = build_flow_report(commits)
    days = [e.day.isoformat() for e in report.entries()]
    assert days == sorted(days)


def test_dominant_type_most_frequent():
    commits = [_c("fix a"), _c("fix b"), _c("add c")]
    report = build_flow_report(commits)
    assert report.dominant_type() == "fix"


def test_flow_entry_str_contains_day():
    report = build_flow_report([_c("feat: something", "2024-03-11")])
    entry_str = str(report.entries()[0])
    assert "2024-03-11" in entry_str


def test_format_flow_report_contains_title():
    report = build_flow_report([_c("feat: x")])
    text = format_flow_report(report, title="MyRepo")
    assert "MyRepo" in text


def test_format_flow_report_empty_shows_no_commits():
    report = build_flow_report([])
    text = format_flow_report(report)
    assert "no commits" in text


# --- flow_integration ---

def test_flow_per_repo_keys_match_input():
    data = {"repo-a": [_c("fix x")], "repo-b": [_c("add y")]}
    result = flow_per_repo(data)
    assert set(result.keys()) == {"repo-a", "repo-b"}


def test_flow_per_repo_totals():
    data = {"repo-a": [_c("fix x"), _c("fix y")], "repo-b": [_c("add z")]}
    result = flow_per_repo(data)
    assert result["repo-a"].total == 2
    assert result["repo-b"].total == 1


def test_combined_flow_total():
    data = {"a": [_c("fix x"), _c("add y")], "b": [_c("remove z")]}
    report = combined_flow(data)
    assert report.total == 3


def test_combined_flow_empty_input():
    report = combined_flow({})
    assert report.total == 0


def test_flow_report_dict_structure():
    data = {"repo-a": [_c("feat: add thing")]}
    d = flow_report_dict(data)
    assert "repos" in d
    assert "combined" in d
    assert "repo-a" in d["repos"]
    assert "dominant_type" in d["combined"]
