"""Tests for gitlog_digest.branch_activity."""
import datetime
import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.branch_activity import (
    BranchActivityReport,
    build_branch_report,
    format_branch_report,
)


def _c(author: str, subject: str = "chore: update") -> GitCommit:
    return GitCommit(
        sha="abc1234",
        author=author,
        date=datetime.datetime(2024, 1, 15, 10, 0, 0),
        subject=subject,
    )


def test_empty_report_has_no_branches():
    report = BranchActivityReport()
    assert len(report) == 0
    assert report.branches == []
    assert report.most_active is None
    assert report.total == 0


def test_add_single_commit_creates_branch_entry():
    report = BranchActivityReport()
    report.add_commit("main", _c("Alice"))
    assert len(report) == 1
    assert report.branches[0].branch == "main"
    assert report.branches[0].commit_count == 1


def test_add_multiple_commits_same_branch_increments_count():
    report = BranchActivityReport()
    report.add_commit("main", _c("Alice"))
    report.add_commit("main", _c("Bob"))
    report.add_commit("main", _c("Alice"))
    assert report.branches[0].commit_count == 3


def test_multiple_branches_tracked_independently():
    report = BranchActivityReport()
    report.add_commit("main", _c("Alice"))
    report.add_commit("feature/x", _c("Bob"))
    report.add_commit("feature/x", _c("Bob"))
    assert len(report) == 2
    assert report.total == 3


def test_branches_sorted_by_commit_count_descending():
    report = BranchActivityReport()
    report.add_commit("main", _c("Alice"))
    report.add_commit("dev", _c("Bob"))
    report.add_commit("dev", _c("Carol"))
    report.add_commit("dev", _c("Alice"))
    branches = report.branches
    assert branches[0].branch == "dev"
    assert branches[1].branch == "main"


def test_most_active_returns_top_branch():
    report = BranchActivityReport()
    report.add_commit("main", _c("Alice"))
    report.add_commit("hotfix", _c("Bob"))
    report.add_commit("hotfix", _c("Bob"))
    assert report.most_active is not None
    assert report.most_active.branch == "hotfix"


def test_build_branch_report_from_dict():
    data = {
        "main": [_c("Alice"), _c("Bob")],
        "feature/y": [_c("Carol")],
    }
    report = build_branch_report(data)
    assert len(report) == 2
    assert report.total == 3


def test_format_branch_report_empty():
    report = BranchActivityReport()
    text = format_branch_report(report)
    assert "No branch activity" in text


def test_format_branch_report_contains_branch_names():
    data = {
        "main": [_c("Alice"), _c("Alice")],
        "dev": [_c("Bob")],
    }
    report = build_branch_report(data)
    text = format_branch_report(report)
    assert "main" in text
    assert "dev" in text
    assert "Most active branch: main" in text


def test_branch_entry_str_unique_authors():
    report = BranchActivityReport()
    report.add_commit("main", _c("Alice"))
    report.add_commit("main", _c("Alice"))
    report.add_commit("main", _c("Bob"))
    entry = report.branches[0]
    result = str(entry)
    assert "Alice" in result
    assert "Bob" in result
    # Alice should appear only once despite two commits
    assert result.count("Alice") == 1
