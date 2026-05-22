"""Tests for commit_recency and recency_integration."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_recency import (
    build_recency_report,
    format_recency_report,
    recency_report_dict,
    _bucket_label,
)
from gitlog_digest.recency_integration import (
    recency_per_repo,
    combined_recency,
    all_recency_report_dicts,
)

_NOW = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


def _c(hours_ago: float, sha: str = "abc1234") -> GitCommit:
    ts = _NOW - timedelta(hours=hours_ago)
    return GitCommit(sha=sha, author="Dev", timestamp=ts, subject="msg")


def test_empty_commits_returns_empty_report():
    report = build_recency_report([], now=_NOW)
    assert report.total() == 0
    assert report.most_recent_bucket() is None


def test_commit_today():
    report = build_recency_report([_c(0.5)], now=_NOW)
    assert report.total() == 1
    assert report.most_recent_bucket() == "Today"


def test_commit_yesterday():
    report = build_recency_report([_c(25)], now=_NOW)
    assert report.most_recent_bucket() == "Yesterday"


def test_commit_this_week():
    report = build_recency_report([_c(72)], now=_NOW)  # 3 days ago
    assert report.most_recent_bucket() == "This week"


def test_commit_older():
    report = build_recency_report([_c(24 * 100)], now=_NOW)  # 100 days ago
    assert report.most_recent_bucket() == "Older"


def test_multiple_commits_accumulate_in_same_bucket():
    commits = [_c(0.1, "a"), _c(0.5, "b"), _c(0.9, "c")]
    report = build_recency_report(commits, now=_NOW)
    assert report.total() == 3
    today_bucket = report._index.get("Today")
    assert today_bucket is not None
    assert today_bucket.count == 3


def test_commits_spread_across_buckets():
    commits = [_c(0.5, "a"), _c(25, "b"), _c(72, "c")]
    report = build_recency_report(commits, now=_NOW)
    assert report.total() == 3
    assert len(report.buckets) == 3


def test_format_recency_report_contains_label():
    report = build_recency_report([_c(0.5)], now=_NOW)
    text = format_recency_report(report)
    assert "Today" in text
    assert "1 commit" in text


def test_format_recency_report_empty():
    report = build_recency_report([], now=_NOW)
    assert format_recency_report(report) == "No commits."


def test_recency_report_dict_structure():
    report = build_recency_report([_c(0.5)], now=_NOW)
    d = recency_report_dict(report)
    assert d["total"] == 1
    assert d["most_recent_bucket"] == "Today"
    assert isinstance(d["buckets"], list)
    assert d["buckets"][0]["label"] == "Today"


def test_recency_per_repo_keys_match_input():
    repo_commits = {
        "repo-a": [_c(1, "a")],
        "repo-b": [_c(50, "b")],
    }
    result = recency_per_repo(repo_commits, now=_NOW)
    assert set(result.keys()) == {"repo-a", "repo-b"}


def test_combined_recency_merges_all_commits():
    repo_commits = {
        "repo-a": [_c(1, "a"), _c(2, "b")],
        "repo-b": [_c(50, "c")],
    }
    combined = combined_recency(repo_commits, now=_NOW)
    assert combined.total() == 3


def test_all_recency_report_dicts_includes_combined():
    repo_commits = {"repo-a": [_c(1, "x")]}
    result = all_recency_report_dicts(repo_commits, now=_NOW)
    assert "__combined__" in result
    assert "repo-a" in result
