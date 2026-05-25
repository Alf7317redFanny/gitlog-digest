"""Tests for commit_cadence and cadence_integration."""
from datetime import datetime, timezone, timedelta
from typing import List

import pytest

from gitlog_digest.commit_cadence import (
    build_cadence_report,
    format_cadence_report,
    CommitCadenceReport,
)
from gitlog_digest.cadence_integration import (
    cadence_per_repo,
    combined_cadence,
    cadence_report_dict,
)
from gitlog_digest.git_reader import GitCommit


def _c(author: str, day_offset: int = 0) -> GitCommit:
    dt = datetime(2024, 3, 4, 12, 0, 0, tzinfo=timezone.utc) + timedelta(days=day_offset)
    return GitCommit(
        sha="abc1234",
        author=author,
        date=dt,
        subject="chore: test",
        files_changed=[],
        insertions=0,
        deletions=0,
        branch="main",
    )


def test_empty_commits_returns_empty_report():
    report = build_cadence_report([])
    assert report.total == 0
    assert report.entries() == []
    assert report.most_regular() is None


def test_single_commit_single_author():
    report = build_cadence_report([_c("alice")])
    assert report.total == 1
    entry = report.entries()[0]
    assert entry.author == "alice"
    assert entry.total_active_days == 1
    assert entry.average_gap is None
    assert entry.regularity_score is None


def test_gaps_computed_correctly():
    commits = [_c("bob", 0), _c("bob", 2), _c("bob", 5)]
    report = build_cadence_report(commits)
    entry = report.entries()[0]
    assert entry.gaps == [2, 3]
    assert entry.average_gap == pytest.approx(2.5)


def test_duplicate_days_deduplicated():
    commits = [_c("alice", 0), _c("alice", 0), _c("alice", 1)]
    report = build_cadence_report(commits)
    entry = report.entries()[0]
    assert entry.total_active_days == 2
    assert entry.gaps == [1]


def test_regularity_score_requires_two_gaps():
    commits = [_c("alice", 0), _c("alice", 3)]
    report = build_cadence_report(commits)
    entry = report.entries()[0]
    assert entry.gaps == [3]
    assert entry.regularity_score is None


def test_most_regular_picks_lowest_stdev():
    commits_alice = [_c("alice", i) for i in [0, 1, 2, 3]]
    commits_bob = [_c("bob", i) for i in [0, 5, 6, 20]]
    report = build_cadence_report(commits_alice + commits_bob)
    most_reg = report.most_regular()
    assert most_reg is not None
    assert most_reg.author == "alice"


def test_format_cadence_report_contains_author():
    report = build_cadence_report([_c("carol", i) for i in range(4)])
    text = format_cadence_report(report)
    assert "carol" in text
    assert "Commit Cadence" in text


def test_cadence_per_repo_keys_match_input():
    repo_commits = {"repo-a": [_c("alice", 0)], "repo-b": [_c("bob", 1)]}
    result = cadence_per_repo(repo_commits)
    assert set(result.keys()) == {"repo-a", "repo-b"}


def test_combined_cadence_merges_authors():
    repo_commits = {
        "repo-a": [_c("alice", i) for i in range(3)],
        "repo-b": [_c("bob", i) for i in range(3)],
    }
    combined = combined_cadence(repo_commits)
    assert combined.total == 2


def test_cadence_report_dict_structure():
    repo_commits = {
        "repo-a": [_c("alice", i) for i in range(5)],
    }
    result = cadence_report_dict(repo_commits)
    assert "repos" in result
    assert "combined" in result
    assert "repo-a" in result["repos"]
    assert "total_authors" in result["combined"]
