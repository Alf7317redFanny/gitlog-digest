"""Tests for gitlog_digest.commit_language."""
from __future__ import annotations

import datetime
from typing import List

import pytest

from gitlog_digest.commit_language import (
    CommitLanguageReport,
    LanguageEntry,
    _detect_language,
    build_language_report,
    merge_reports,
)
from gitlog_digest.git_reader import GitCommit


def _c(
    sha: str = "abc1234",
    subject: str = "chore: update",
    author: str = "Alice",
    date: datetime.datetime = datetime.datetime(2024, 3, 4, 10, 0),
    files: List[str] | None = None,
) -> GitCommit:
    return GitCommit(
        sha=sha,
        subject=subject,
        author=author,
        date=date,
        files_changed=files or [],
    )


# --- _detect_language ---

def test_detect_language_python():
    assert _detect_language("main.py") == "Python"


def test_detect_language_typescript():
    assert _detect_language("app.ts") == "TypeScript"


def test_detect_language_case_insensitive():
    assert _detect_language("Script.PY") == "Python"


def test_detect_language_no_extension_returns_none():
    assert _detect_language("Makefile") is None


def test_detect_language_unknown_extension_returns_none():
    assert _detect_language("file.xyz") is None


def test_detect_language_multiple_dots_uses_last():
    assert _detect_language("archive.tar.gz") is None
    assert _detect_language("component.test.js") == "JavaScript"


# --- CommitLanguageReport ---

def test_empty_report_has_no_entries():
    report = CommitLanguageReport()
    assert len(report) == 0
    assert report.top() == []


def test_add_commit_single_language():
    report = CommitLanguageReport()
    report.add_commit(_c(files=["src/main.py", "tests/test_main.py"]))
    assert len(report) == 1
    entry = report.entry_for("Python")
    assert entry is not None
    assert entry.commit_count == 1
    assert entry.file_count == 2


def test_add_commit_multiple_languages():
    report = CommitLanguageReport()
    report.add_commit(_c(files=["app.py", "style.css"]))
    assert len(report) == 2
    assert report.entry_for("Python").commit_count == 1
    assert report.entry_for("CSS").commit_count == 1


def test_two_commits_same_language_increments_count():
    report = CommitLanguageReport()
    report.add_commit(_c(sha="aaa", files=["a.py"]))
    report.add_commit(_c(sha="bbb", files=["b.py"]))
    entry = report.entry_for("Python")
    assert entry.commit_count == 2
    assert entry.file_count == 2


def test_unrecognised_files_not_counted():
    report = CommitLanguageReport()
    report.add_commit(_c(files=["Makefile", "README.md", "data.csv"]))
    assert len(report) == 0


def test_top_returns_sorted_by_commit_count():
    report = CommitLanguageReport()
    for _ in range(3):
        report.add_commit(_c(files=["a.py"]))
    report.add_commit(_c(files=["b.js"]))
    top = report.top(2)
    assert top[0].language == "Python"
    assert top[1].language == "JavaScript"


def test_top_n_larger_than_entries_returns_all():
    report = CommitLanguageReport()
    report.add_commit(_c(files=["a.py"]))
    assert len(report.top(100)) == 1


def test_build_language_report_convenience():
    commits = [_c(files=["x.go"]), _c(files=["y.go", "z.rs"])]
    report = build_language_report(commits)
    assert report.entry_for("Go").commit_count == 2
    assert report.entry_for("Rust").commit_count == 1


# --- merge_reports ---

def test_merge_reports_combines_counts():
    r1 = build_language_report([_c(files=["a.py"])])
    r2 = build_language_report([_c(files=["b.py", "c.js"])])
    merged = merge_reports(r1, r2)
    assert merged.entry_for("Python").commit_count == 2
    assert merged.entry_for("JavaScript").commit_count == 1


def test_merge_empty_reports_returns_empty():
    merged = merge_reports(CommitLanguageReport(), CommitLanguageReport())
    assert len(merged) == 0
