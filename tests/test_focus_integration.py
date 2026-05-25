"""Tests for gitlog_digest.focus_integration."""
from __future__ import annotations

from datetime import datetime

from gitlog_digest.focus_integration import (
    combined_focus,
    focus_per_repo,
    focus_report_dict,
    format_all_focus_reports,
)
from gitlog_digest.git_reader import GitCommit


def _c(
    sha: str = "abc",
    author: str = "Alice",
    files: list | None = None,
) -> GitCommit:
    return GitCommit(
        sha=sha,
        author=author,
        date=datetime(2024, 6, 3),
        subject="feat: something",
        files_changed=files or [],
        insertions=2,
        deletions=1,
    )


def test_focus_per_repo_keys_match_input():
    data = {
        "repo-a": [_c(sha="1", files=["src/a.py"])],
        "repo-b": [_c(sha="2", files=["lib/b.py"])],
    }
    result = focus_per_repo(data)
    assert set(result.keys()) == {"repo-a", "repo-b"}


def test_focus_per_repo_counts_are_independent():
    data = {
        "repo-a": [_c(sha="1", files=["src/a.py"]), _c(sha="2", files=["src/b.py"])],
        "repo-b": [_c(sha="3", files=["src/c.py"])],
    }
    result = focus_per_repo(data)
    assert result["repo-a"].top()[0].commit_count == 2
    assert result["repo-b"].top()[0].commit_count == 1


def test_combined_focus_merges_all():
    data = {
        "repo-a": [_c(sha="1", files=["src/a.py"])],
        "repo-b": [_c(sha="2", files=["src/b.py"])],
    }
    report = combined_focus(data)
    assert report.top()[0].commit_count == 2


def test_combined_focus_empty_input():
    report = combined_focus({})
    assert report.total_directories == 0


def test_focus_report_dict_structure():
    data = {"repo-a": [_c(sha="1", files=["src/a.py"])]}
    report = combined_focus(data)
    d = focus_report_dict(report)
    assert "total_directories" in d
    assert "top" in d
    assert d["top"][0]["directory"] == "src"
    assert d["top"][0]["commit_count"] == 1
    assert "unique_authors" in d["top"][0]


def test_format_all_focus_reports_contains_repo_name():
    data = {"my-repo": [_c(sha="1", files=["src/a.py"])]}
    output = format_all_focus_reports(data)
    assert "my-repo" in output


def test_format_all_focus_reports_contains_combined():
    data = {"my-repo": [_c(sha="1", files=["src/a.py"])]}
    output = format_all_focus_reports(data)
    assert "combined" in output


def test_format_all_focus_reports_empty_repo():
    output = format_all_focus_reports({"empty-repo": []})
    assert "no directory-level data" in output
