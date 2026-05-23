"""Tests for commit_revert and revert_integration."""
from __future__ import annotations

import datetime
from typing import List

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_revert import (
    build_revert_report,
    format_revert_report,
    _extract_reverted_subject,
    _extract_reverted_sha,
)
from gitlog_digest.revert_integration import (
    reverts_per_repo,
    combined_revert,
    revert_report_dict,
)

_DATE = datetime.datetime(2024, 3, 11, 10, 0, 0)


def _c(sha: str, subject: str, author: str = "Alice", body: str = "") -> GitCommit:
    c = GitCommit(sha=sha, author=author, date=_DATE, subject=subject)
    c.body = body  # type: ignore[attr-defined]
    return c


def test_extract_reverted_subject_quoted():
    assert _extract_reverted_subject('Revert "add login feature"') == "add login feature"


def test_extract_reverted_subject_unquoted():
    assert _extract_reverted_subject("Revert add login feature") == "add login feature"


def test_extract_reverted_subject_non_revert_returns_none():
    assert _extract_reverted_subject("feat: add login") is None


def test_extract_reverted_sha_present():
    body = "This reverts commit abc1234def5678."
    assert _extract_reverted_sha(body) == "abc1234"


def test_extract_reverted_sha_missing():
    assert _extract_reverted_sha("some body text") is None


def test_empty_commits_returns_empty_report():
    report = build_revert_report([])
    assert report.total == 0
    assert report.entries() == []


def test_non_revert_commits_not_counted():
    commits = [_c("aaa1111", "feat: add thing"), _c("bbb2222", "fix: patch")]
    report = build_revert_report(commits)
    assert report.total == 0


def test_revert_commit_counted():
    commits = [_c("ccc3333", 'Revert "feat: add thing"')]
    report = build_revert_report(commits)
    assert report.total == 1


def test_revert_entry_extracts_subject():
    commits = [_c("ddd4444", 'Revert "fix: patch bug"')]
    report = build_revert_report(commits)
    assert report.entries()[0].reverted_subject == "fix: patch bug"


def test_revert_entry_extracts_sha_from_body():
    body = "This reverts commit deadbeef1234567."
    commits = [_c("eee5555", 'Revert "some change"', body=body)]
    report = build_revert_report(commits)
    assert report.entries()[0].reverted_sha == "deadbee"


def test_multiple_reverts_all_counted():
    commits = [
        _c("f1", 'Revert "alpha"'),
        _c("f2", 'Revert "beta"'),
        _c("f3", "fix: unrelated"),
    ]
    report = build_revert_report(commits)
    assert report.total == 2


def test_format_revert_report_empty():
    report = build_revert_report([])
    assert "none" in format_revert_report(report)


def test_format_revert_report_non_empty():
    commits = [_c("abc1234", 'Revert "fix: bug"', author="Bob")]
    report = build_revert_report(commits)
    text = format_revert_report(report)
    assert "Bob" in text
    assert "1 total" in text


def test_reverts_per_repo_keys():
    data = {
        "repo-a": [_c("a1", 'Revert "x"')],
        "repo-b": [_c("b1", "feat: y")],
    }
    result = reverts_per_repo(data)
    assert set(result.keys()) == {"repo-a", "repo-b"}
    assert result["repo-a"].total == 1
    assert result["repo-b"].total == 0


def test_combined_revert_merges_all():
    data = {
        "repo-a": [_c("a1", 'Revert "x"')],
        "repo-b": [_c("b1", 'Revert "y"')],
    }
    report = combined_revert(data)
    assert report.total == 2


def test_revert_report_dict_structure():
    commits = [_c("abc1234", 'Revert "feat: thing"', author="Carol")]
    report = build_revert_report(commits)
    d = revert_report_dict(report)
    assert d["total_reverts"] == 1
    assert d["entries"][0]["author"] == "Carol"
    assert d["entries"][0]["sha"] == "abc1234"[:7]
