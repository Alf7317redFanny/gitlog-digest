"""Tests for gitlog_digest.commit_focus."""
from __future__ import annotations

from datetime import datetime

import pytest

from gitlog_digest.commit_focus import (
    CommitFocusReport,
    FocusEntry,
    _top_dir,
    build_focus_report,
)
from gitlog_digest.git_reader import GitCommit


def _c(
    sha: str = "abc",
    author: str = "Alice",
    files: list | None = None,
    subject: str = "chore: update",
) -> GitCommit:
    return GitCommit(
        sha=sha,
        author=author,
        date=datetime(2024, 6, 3),
        subject=subject,
        files_changed=files or [],
        insertions=0,
        deletions=0,
    )


def test_top_dir_nested():
    assert _top_dir("src/module/file.py") == "src"


def test_top_dir_root_file_returns_none():
    assert _top_dir("README.md") is None


def test_top_dir_one_level_deep():
    assert _top_dir("docs/index.md") == "docs"


def test_empty_commits_returns_empty_report():
    report = build_focus_report([])
    assert report.total_directories == 0
    assert report.top() == []


def test_single_commit_single_dir():
    report = build_focus_report([_c(files=["src/main.py"])])
    assert report.total_directories == 1
    top = report.top()
    assert top[0].directory == "src"
    assert top[0].commit_count == 1


def test_root_file_not_counted():
    report = build_focus_report([_c(files=["README.md"])])
    assert report.total_directories == 0


def test_multiple_commits_same_dir_increments():
    commits = [
        _c(sha="a", files=["src/a.py"]),
        _c(sha="b", files=["src/b.py"]),
    ]
    report = build_focus_report(commits)
    assert report.top()[0].commit_count == 2


def test_multiple_dirs_sorted_by_count():
    commits = [
        _c(sha="a", files=["src/a.py"]),
        _c(sha="b", files=["src/b.py"]),
        _c(sha="c", files=["docs/x.md"]),
    ]
    report = build_focus_report(commits)
    top = report.top()
    assert top[0].directory == "src"
    assert top[1].directory == "docs"


def test_unique_authors_tracked():
    commits = [
        _c(sha="a", author="Alice", files=["src/a.py"]),
        _c(sha="b", author="Bob", files=["src/b.py"]),
        _c(sha="c", author="Alice", files=["src/c.py"]),
    ]
    report = build_focus_report(commits)
    entry = report.top()[0]
    assert entry.unique_authors == 2


def test_top_n_limits_results():
    commits = [_c(sha=str(i), files=[f"dir{i}/f.py"]) for i in range(20)]
    report = build_focus_report(commits)
    assert len(report.top(5)) == 5


def test_merge_combines_counts():
    r1 = build_focus_report([_c(sha="a", files=["src/a.py"])])
    r2 = build_focus_report([_c(sha="b", files=["src/b.py"])])
    merged = r1.merge(r2)
    assert merged.top()[0].commit_count == 2


def test_merge_combines_authors():
    r1 = build_focus_report([_c(sha="a", author="Alice", files=["src/a.py"])])
    r2 = build_focus_report([_c(sha="b", author="Bob", files=["src/b.py"])])
    merged = r1.merge(r2)
    assert merged.top()[0].unique_authors == 2
