"""Tests for gitlog_digest.commit_churn."""
from __future__ import annotations

import datetime
import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_churn import (
    build_churn_report,
    churn_report_dict,
    format_churn_report,
    CommitChurnReport,
    ChurnEntry,
)


def _c(files: list[str], sha: str = "abc1234") -> GitCommit:
    return GitCommit(
        sha=sha,
        author="Dev",
        date=datetime.datetime(2024, 3, 1, 10, 0),
        subject="chore: update stuff",
        files_changed=files,
    )


def test_empty_commits_returns_empty_report():
    report = build_churn_report([])
    assert report.total_files == 0
    assert report.total_touches == 0
    assert report.top() == []


def test_single_commit_single_file():
    report = build_churn_report([_c(["src/main.py"])])
    assert report.total_files == 1
    assert report.total_touches == 1
    assert report.top()[0].filepath == "src/main.py"
    assert report.top()[0].count == 1


def test_multiple_commits_same_file_increments_count():
    commits = [
        _c(["src/main.py"], sha="aaa"),
        _c(["src/main.py"], sha="bbb"),
        _c(["src/main.py"], sha="ccc"),
    ]
    report = build_churn_report(commits)
    assert report.total_files == 1
    assert report.total_touches == 3
    assert report.top()[0].count == 3


def test_multiple_files_sorted_by_frequency():
    commits = [
        _c(["a.py", "b.py"], sha="1"),
        _c(["a.py", "c.py"], sha="2"),
        _c(["a.py"], sha="3"),
    ]
    report = build_churn_report(commits)
    top = report.top(3)
    assert top[0].filepath == "a.py"
    assert top[0].count == 3


def test_top_n_limits_results():
    files = [f"file{i}.py" for i in range(20)]
    commits = [_c([f], sha=f"sha{i}") for i, f in enumerate(files)]
    report = build_churn_report(commits)
    assert len(report.top(5)) == 5


def test_len_returns_total_files():
    report = build_churn_report([_c(["x.py", "y.py"])])
    assert len(report) == 2


def test_churn_entry_str():
    entry = ChurnEntry(filepath="src/utils.py", count=7)
    assert str(entry) == "src/utils.py (7 commits)"


def test_format_churn_report_empty():
    report = build_churn_report([])
    text = format_churn_report(report)
    assert "No file churn" in text


def test_format_churn_report_contains_filename():
    report = build_churn_report([_c(["README.md"])])
    text = format_churn_report(report)
    assert "README.md" in text


def test_churn_report_dict_structure():
    report = build_churn_report([_c(["setup.cfg", "README.md"]), _c(["setup.cfg"], sha="xyz")])
    d = churn_report_dict(report)
    assert d["total_files"] == 2
    assert d["total_touches"] == 3
    assert d["top_files"][0]["filepath"] == "setup.cfg"
    assert d["top_files"][0]["count"] == 2
