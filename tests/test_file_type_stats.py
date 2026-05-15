"""Tests for gitlog_digest.file_type_stats."""
from datetime import datetime

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.file_type_stats import (
    FileTypeReport,
    build_file_type_report,
    file_type_report_dict,
    _extract_extension,
)


def _c(author: str, files: list) -> GitCommit:
    c = GitCommit(
        sha="abc1234",
        author=author,
        date=datetime(2024, 3, 4),
        subject="chore: update",
    )
    c.files = files
    return c


# --- _extract_extension ---

def test_extract_extension_simple():
    assert _extract_extension("main.py") == "py"


def test_extract_extension_uppercase_normalised():
    assert _extract_extension("README.MD") == "md"


def test_extract_extension_no_dot():
    assert _extract_extension("Makefile") == ""


def test_extract_extension_multiple_dots():
    assert _extract_extension("archive.tar.gz") == "gz"


# --- build_file_type_report ---

def test_empty_commits_returns_empty_report():
    report = build_file_type_report([])
    assert report.total_extensions == 0
    assert report.top() == []


def test_single_commit_single_extension():
    report = build_file_type_report([_c("alice", ["foo.py", "bar.py"])])
    entry = report.entry_for("py")
    assert entry.commit_count == 1
    assert entry.authors == ["alice"]


def test_multiple_commits_same_extension():
    commits = [
        _c("alice", ["a.py"]),
        _c("bob", ["b.py"]),
    ]
    report = build_file_type_report(commits)
    entry = report.entry_for("py")
    assert entry.commit_count == 2
    assert set(entry.authors) == {"alice", "bob"}


def test_each_extension_counted_once_per_commit():
    """Two .py files in one commit should only count as 1 commit for 'py'."""
    report = build_file_type_report([_c("alice", ["a.py", "b.py", "c.md"])])
    assert report.entry_for("py").commit_count == 1
    assert report.entry_for("md").commit_count == 1


def test_top_returns_sorted_by_count():
    commits = [
        _c("alice", ["a.py"]),
        _c("alice", ["b.py"]),
        _c("bob", ["c.md"]),
    ]
    report = build_file_type_report(commits)
    top = report.top(2)
    assert top[0].extension == "py"
    assert top[0].commit_count == 2


def test_file_without_extension_grouped_under_empty():
    report = build_file_type_report([_c("alice", ["Makefile"])])
    entry = report.entry_for("")
    assert entry.commit_count == 1


def test_file_type_report_dict_structure():
    commits = [_c("alice", ["main.py"]), _c("bob", ["app.js"])]
    report = build_file_type_report(commits)
    d = file_type_report_dict(report)
    assert "total_extensions" in d
    assert "top" in d
    assert d["total_extensions"] == 2
    assert all("extension" in item for item in d["top"])


def test_entry_str_includes_extension_and_count():
    commits = [_c("alice", ["a.py"]), _c("bob", ["b.py"])]
    report = build_file_type_report(commits)
    text = str(report.entry_for("py"))
    assert "py" in text
    assert "2" in text
