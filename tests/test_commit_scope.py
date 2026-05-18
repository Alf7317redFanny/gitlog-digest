"""Tests for commit_scope.py."""

from __future__ import annotations

from datetime import datetime
from typing import List

import pytest

from gitlog_digest.commit_scope import (
    CommitScopeReport,
    build_scope_report,
    format_scope_report,
    scope_report_dict,
    _top_level_scope,
)
from gitlog_digest.git_reader import GitCommit


def _c(files: List[str], sha: str = "abc1234", author: str = "Alice") -> GitCommit:
    return GitCommit(
        sha=sha,
        author=author,
        date=datetime(2024, 6, 3, 10, 0, 0),
        subject="chore: update stuff",
        files_changed=files,
    )


def test_top_level_scope_nested_path():
    assert _top_level_scope("src/utils/helper.py") == "src"


def test_top_level_scope_root_file():
    assert _top_level_scope("README.md") == "."


def test_top_level_scope_two_levels():
    assert _top_level_scope("tests/test_foo.py") == "tests"


def test_empty_commits_returns_empty_report():
    report = build_scope_report([])
    assert len(report) == 0
    assert report.total_files == 0
    assert report.scopes() == []


def test_single_commit_single_scope():
    commit = _c(["src/main.py", "src/utils.py"])
    report = build_scope_report([commit])
    assert len(report) == 1
    entry = report.scopes()[0]
    assert entry.scope == "src"
    assert entry.file_count == 2
    assert entry.commit_count == 1


def test_multiple_commits_same_scope_accumulates():
    commits = [
        _c(["src/a.py"], sha="aaa"),
        _c(["src/b.py"], sha="bbb"),
    ]
    report = build_scope_report(commits)
    assert len(report) == 1
    entry = report.scopes()[0]
    assert entry.commit_count == 2
    assert entry.file_count == 2


def test_multiple_scopes_sorted_by_commit_count():
    commits = [
        _c(["docs/readme.md"], sha="d1"),
        _c(["src/a.py", "src/b.py"], sha="s1"),
        _c(["src/c.py"], sha="s2"),
    ]
    report = build_scope_report(commits)
    scopes = report.scopes()
    assert scopes[0].scope == "src"
    assert scopes[1].scope == "docs"


def test_root_files_grouped_under_dot():
    commit = _c(["Makefile", "setup.cfg"])
    report = build_scope_report([commit])
    assert "." in [e.scope for e in report.scopes()]


def test_top_returns_at_most_n():
    commits = [_c([f"dir{i}/file.py"], sha=f"sha{i}") for i in range(10)]
    report = build_scope_report(commits)
    assert len(report.top(3)) == 3


def test_scope_report_dict_structure():
    commit = _c(["src/main.py"])
    report = build_scope_report([commit])
    d = scope_report_dict(report)
    assert "total_scopes" in d
    assert "total_files" in d
    assert isinstance(d["scopes"], list)
    assert d["scopes"][0]["scope"] == "src"


def test_format_scope_report_empty():
    report = CommitScopeReport()
    text = format_scope_report(report)
    assert "No scope data" in text


def test_format_scope_report_non_empty():
    commit = _c(["src/main.py"])
    report = build_scope_report([commit])
    text = format_scope_report(report)
    assert "src" in text
    assert "Commit Scope Breakdown" in text
