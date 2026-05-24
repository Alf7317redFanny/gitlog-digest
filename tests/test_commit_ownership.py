"""Tests for commit_ownership module."""
import pytest
from datetime import datetime

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_ownership import (
    build_ownership_report,
    format_ownership_report,
    CommitOwnershipReport,
)


def _c(author: str, files: list) -> GitCommit:
    return GitCommit(
        sha="abc1234",
        author=author,
        date=datetime(2024, 6, 3, 10, 0, 0),
        subject="chore: update",
        files_changed=files,
    )


def test_empty_commits_returns_empty_report():
    report = build_ownership_report([])
    assert report.total_files() == 0
    assert report.top() == []


def test_single_commit_single_file():
    report = build_ownership_report([_c("alice", ["src/main.py"])])
    assert report.total_files() == 1
    entry = report.entry_for("src/main.py")
    assert entry is not None
    assert entry.owner == "alice"
    assert entry.owner_count == 1
    assert entry.total_commits == 1


def test_multiple_commits_same_file_same_author():
    commits = [
        _c("alice", ["src/main.py"]),
        _c("alice", ["src/main.py"]),
        _c("alice", ["src/main.py"]),
    ]
    report = build_ownership_report(commits)
    entry = report.entry_for("src/main.py")
    assert entry.owner == "alice"
    assert entry.owner_count == 3
    assert entry.ownership_ratio == 1.0


def test_owner_is_most_frequent_author():
    commits = [
        _c("alice", ["src/app.py"]),
        _c("alice", ["src/app.py"]),
        _c("bob", ["src/app.py"]),
    ]
    report = build_ownership_report(commits)
    entry = report.entry_for("src/app.py")
    assert entry.owner == "alice"
    assert entry.owner_count == 2
    assert entry.total_commits == 3


def test_ownership_ratio_calculated_correctly():
    commits = [
        _c("alice", ["lib/util.py"]),
        _c("bob", ["lib/util.py"]),
        _c("bob", ["lib/util.py"]),
        _c("bob", ["lib/util.py"]),
    ]
    report = build_ownership_report(commits)
    entry = report.entry_for("lib/util.py")
    assert entry.owner == "bob"
    assert abs(entry.ownership_ratio - 0.75) < 1e-9


def test_entry_for_unknown_file_returns_none():
    report = build_ownership_report([_c("alice", ["src/main.py"])])
    assert report.entry_for("nonexistent.py") is None


def test_top_returns_sorted_by_total_commits():
    commits = [
        _c("alice", ["a.py", "b.py"]),
        _c("alice", ["a.py"]),
        _c("bob", ["b.py"]),
    ]
    report = build_ownership_report(commits)
    top = report.top(2)
    assert top[0].filepath in ("a.py", "b.py")
    assert top[0].total_commits >= top[1].total_commits


def test_contested_files_below_threshold():
    commits = [
        _c("alice", ["shared.py"]),
        _c("bob", ["shared.py"]),
        _c("carol", ["shared.py"]),
    ]
    report = build_ownership_report(commits)
    contested = report.contested_files(threshold=0.6)
    assert any(e.filepath == "shared.py" for e in contested)


def test_uncontested_file_not_in_contested():
    commits = [
        _c("alice", ["owned.py"]),
        _c("alice", ["owned.py"]),
        _c("alice", ["owned.py"]),
        _c("bob", ["owned.py"]),
    ]
    report = build_ownership_report(commits)
    contested = report.contested_files(threshold=0.6)
    assert not any(e.filepath == "owned.py" for e in contested)


def test_format_ownership_report_non_empty():
    commits = [_c("alice", ["src/main.py"]), _c("bob", ["src/main.py"])]
    report = build_ownership_report(commits)
    text = format_ownership_report(report)
    assert "File Ownership" in text
    assert "src/main.py" in text


def test_format_ownership_report_empty():
    report = build_ownership_report([])
    text = format_ownership_report(report)
    assert "no data" in text
