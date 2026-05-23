"""Tests for gitlog_digest.language_integration."""
from __future__ import annotations

import datetime
from typing import List

import pytest

from gitlog_digest.language_integration import (
    combined_report,
    format_all_language_reports,
    language_report_dict,
    reports_per_repo,
)
from gitlog_digest.git_reader import GitCommit


def _c(
    sha: str = "abc1234",
    subject: str = "fix: something",
    author: str = "Dev",
    date: datetime.datetime = datetime.datetime(2024, 3, 4, 9, 0),
    files: List[str] | None = None,
) -> GitCommit:
    return GitCommit(
        sha=sha,
        subject=subject,
        author=author,
        date=date,
        files_changed=files or [],
    )


def test_reports_per_repo_keys_match_input():
    repo_commits = {
        "api": [_c(files=["server.py"])],
        "frontend": [_c(files=["app.ts"])],
    }
    result = reports_per_repo(repo_commits)
    assert set(result.keys()) == {"api", "frontend"}


def test_reports_per_repo_are_independent():
    repo_commits = {
        "api": [_c(files=["a.py"])],
        "frontend": [_c(files=["b.js"])],
    }
    result = reports_per_repo(repo_commits)
    assert result["api"].entry_for("Python") is not None
    assert result["api"].entry_for("JavaScript") is None
    assert result["frontend"].entry_for("JavaScript") is not None


def test_combined_report_merges_languages():
    repo_commits = {
        "api": [_c(files=["a.py"]), _c(files=["b.py"])],
        "frontend": [_c(files=["c.py", "d.ts"])],
    }
    report = combined_report(repo_commits)
    py_entry = report.entry_for("Python")
    assert py_entry is not None
    assert py_entry.commit_count == 3


def test_combined_report_empty_input():
    report = combined_report({})
    assert len(report) == 0


def test_language_report_dict_structure():
    repo_commits = {"svc": [_c(files=["main.go", "util.go"])]}
    report = combined_report(repo_commits)
    d = language_report_dict(report)
    assert "top_languages" in d
    assert "total_languages_detected" in d
    assert d["total_languages_detected"] == 1
    assert d["top_languages"][0]["language"] == "Go"


def test_language_report_dict_top_n_respected():
    repo_commits = {
        "r": [
            _c(files=["a.py"]),
            _c(files=["b.js"]),
            _c(files=["c.ts"]),
            _c(files=["d.go"]),
        ]
    }
    report = combined_report(repo_commits)
    d = language_report_dict(report, top_n=2)
    assert len(d["top_languages"]) == 2


def test_format_all_language_reports_contains_repo_name():
    repo_commits = {"myrepo": [_c(files=["main.py"])]}
    text = format_all_language_reports(repo_commits)
    assert "myrepo" in text
    assert "Python" in text


def test_format_all_language_reports_no_languages_message():
    repo_commits = {"empty": [_c(files=["Makefile", "README"])]}
    text = format_all_language_reports(repo_commits)
    assert "no recognised languages" in text
