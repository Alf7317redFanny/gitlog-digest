"""Tests for gitlog_digest.diff_stats."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gitlog_digest.diff_stats import (
    DiffStat,
    DiffSummary,
    compute_diff_summary,
    fetch_diff_stat,
)
from gitlog_digest.git_reader import GitCommit
from datetime import datetime


def _commit(sha: str) -> GitCommit:
    return GitCommit(sha=sha, author="Alice", date=datetime(2024, 3, 4), subject="msg")


GIT_OUTPUT_BOTH = """
 3 files changed, 12 insertions(+), 5 deletions(-)
"""

GIT_OUTPUT_INSERT_ONLY = """
 1 file changed, 7 insertions(+)
"""

GIT_OUTPUT_EMPTY = ""


@patch("gitlog_digest.diff_stats.subprocess.run")
def test_fetch_diff_stat_both(mock_run):
    mock_run.return_value = MagicMock(stdout=GIT_OUTPUT_BOTH)
    stat = fetch_diff_stat("abc123", Path("/repo"))
    assert stat.sha == "abc123"
    assert stat.insertions == 12
    assert stat.deletions == 5
    assert stat.net == 7
    assert stat.total_changes == 17


@patch("gitlog_digest.diff_stats.subprocess.run")
def test_fetch_diff_stat_insertions_only(mock_run):
    mock_run.return_value = MagicMock(stdout=GIT_OUTPUT_INSERT_ONLY)
    stat = fetch_diff_stat("def456", Path("/repo"))
    assert stat.insertions == 7
    assert stat.deletions == 0


@patch("gitlog_digest.diff_stats.subprocess.run")
def test_fetch_diff_stat_empty(mock_run):
    mock_run.return_value = MagicMock(stdout=GIT_OUTPUT_EMPTY)
    stat = fetch_diff_stat("000000", Path("/repo"))
    assert stat.insertions == 0
    assert stat.deletions == 0


def test_diff_summary_totals():
    stats = [
        DiffStat(sha="a", insertions=10, deletions=2),
        DiffStat(sha="b", insertions=5, deletions=8),
    ]
    summary = DiffSummary(stats=stats)
    assert summary.total_insertions == 15
    assert summary.total_deletions == 10
    assert summary.total_changes == 25


def test_diff_summary_most_changed():
    stats = [
        DiffStat(sha="a", insertions=1, deletions=1),
        DiffStat(sha="b", insertions=50, deletions=30),
    ]
    summary = DiffSummary(stats=stats)
    assert summary.most_changed_commit is not None
    assert summary.most_changed_commit.sha == "b"


def test_diff_summary_empty():
    summary = DiffSummary(stats=[])
    assert summary.total_changes == 0
    assert summary.most_changed_commit is None


@patch("gitlog_digest.diff_stats.fetch_diff_stat")
def test_compute_diff_summary(mock_fetch):
    mock_fetch.side_effect = [
        DiffStat(sha="sha1", insertions=3, deletions=1),
        DiffStat(sha="sha2", insertions=6, deletions=2),
    ]
    commits = [_commit("sha1"), _commit("sha2")]
    summary = compute_diff_summary(commits, Path("/repo"))
    assert len(summary.stats) == 2
    assert summary.total_insertions == 9
