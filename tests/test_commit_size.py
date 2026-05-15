"""Tests for gitlog_digest.commit_size."""

import pytest
from datetime import datetime
from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_size import (
    build_size_report,
    format_size_report,
    SMALL_MAX,
    MEDIUM_MAX,
    LARGE_MAX,
)


def _c(insertions: int = 0, deletions: int = 0) -> GitCommit:
    return GitCommit(
        sha="abc1234",
        author="Alice",
        date=datetime(2024, 6, 3, 10, 0, 0),
        message="chore: update stuff",
        insertions=insertions,
        deletions=deletions,
    )


def test_empty_commits_returns_empty_report():
    report = build_size_report([])
    assert report.total == 0
    assert len(report.small) == 0
    assert len(report.medium) == 0
    assert len(report.large) == 0
    assert len(report.xlarge) == 0


def test_small_commit_boundary():
    report = build_size_report([_c(insertions=5, deletions=5)])  # exactly 10
    assert len(report.small) == 1
    assert report.total == 1


def test_commit_just_above_small_goes_to_medium():
    report = build_size_report([_c(insertions=6, deletions=5)])  # 11 lines
    assert len(report.medium) == 1
    assert len(report.small) == 0


def test_medium_commit_boundary():
    report = build_size_report([_c(insertions=30, deletions=20)])  # exactly 50
    assert len(report.medium) == 1


def test_large_commit():
    report = build_size_report([_c(insertions=100, deletions=50)])  # 150 lines
    assert len(report.large) == 1


def test_xlarge_commit():
    report = build_size_report([_c(insertions=500, deletions=100)])  # 600 lines
    assert len(report.xlarge) == 1


def test_large_boundary():
    report = build_size_report([_c(insertions=100, deletions=100)])  # exactly 200
    assert len(report.large) == 1


def test_mixed_commits_distributed_correctly():
    commits = [
        _c(insertions=2, deletions=3),    # 5  -> small
        _c(insertions=20, deletions=10),   # 30 -> medium
        _c(insertions=80, deletions=80),   # 160 -> large
        _c(insertions=300, deletions=50),  # 350 -> xlarge
    ]
    report = build_size_report(commits)
    assert len(report.small) == 1
    assert len(report.medium) == 1
    assert len(report.large) == 1
    assert len(report.xlarge) == 1
    assert report.total == 4


def test_as_dict_returns_correct_keys():
    report = build_size_report([_c(insertions=1)])
    d = report.as_dict()
    assert set(d.keys()) == {"small", "medium", "large", "xlarge"}


def test_as_dict_counts_match():
    commits = [_c(insertions=2), _c(insertions=2), _c(insertions=100)]
    report = build_size_report(commits)
    d = report.as_dict()
    assert d["small"] == 2
    assert d["large"] == 1


def test_format_size_report_contains_labels():
    report = build_size_report([_c(insertions=5)])
    text = format_size_report(report)
    assert "small" in text
    assert "medium" in text
    assert "large" in text
    assert "xlarge" in text


def test_format_size_report_shows_commit_count():
    report = build_size_report([_c(insertions=5), _c(insertions=5)])
    text = format_size_report(report)
    assert "2 commit(s)" in text
