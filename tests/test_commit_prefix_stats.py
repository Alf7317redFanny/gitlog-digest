"""Tests for gitlog_digest.commit_prefix_stats."""

import pytest
from datetime import datetime

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_prefix_stats import (
    CommitPrefixReport,
    PrefixEntry,
    build_prefix_report,
    format_prefix_report,
    _extract_prefix,
)


def _c(subject: str, sha: str = "abc1234") -> GitCommit:
    return GitCommit(
        sha=sha,
        subject=subject,
        author="Dev",
        date=datetime(2024, 6, 3, 10, 0, 0),
        files_changed=[],
        insertions=0,
        deletions=0,
        branch="main",
    )


def test_extract_prefix_feat_colon():
    assert _extract_prefix("feat: add login") == "feat"


def test_extract_prefix_fix_with_scope():
    assert _extract_prefix("fix(auth): correct token expiry") == "fix"


def test_extract_prefix_unknown_returns_none():
    assert _extract_prefix("initial commit") is None


def test_extract_prefix_case_insensitive():
    assert _extract_prefix("FEAT: uppercase prefix") == "feat"


def test_extract_prefix_wip():
    assert _extract_prefix("wip: halfway done") == "wip"


def test_empty_commits_returns_empty_report():
    report = build_prefix_report([])
    assert report.total == 0
    assert report.top() == []


def test_single_feat_commit():
    report = build_prefix_report([_c("feat: new feature")])
    assert report.total == 1
    top = report.top()
    assert len(top) == 1
    assert top[0].prefix == "feat"
    assert top[0].count == 1


def test_multiple_commits_same_prefix():
    commits = [_c("fix: bug one"), _c("fix: bug two"), _c("fix: bug three")]
    report = build_prefix_report(commits)
    assert report.total == 3
    assert report.top(1)[0].count == 3


def test_mixed_prefixes_sorted_by_count():
    commits = [
        _c("feat: a"), _c("feat: b"), _c("feat: c"),
        _c("fix: x"), _c("fix: y"),
        _c("chore: z"),
    ]
    report = build_prefix_report(commits)
    top = report.top(3)
    assert top[0].prefix == "feat"
    assert top[1].prefix == "fix"
    assert top[2].prefix == "chore"


def test_unprefixed_commits_not_counted():
    commits = [_c("update readme"), _c("feat: something")]
    report = build_prefix_report(commits)
    assert report.total == 1


def test_as_dict_returns_mapping():
    commits = [_c("docs: update readme"), _c("docs: fix typo"), _c("test: add unit tests")]
    report = build_prefix_report(commits)
    d = report.as_dict()
    assert d["docs"] == 2
    assert d["test"] == 1


def test_format_prefix_report_contains_prefix_name():
    commits = [_c("feat: something cool")]
    report = build_prefix_report(commits)
    text = format_prefix_report(report)
    assert "feat" in text


def test_format_prefix_report_empty_shows_fallback():
    report = build_prefix_report([])
    text = format_prefix_report(report)
    assert "no conventional prefixes" in text


def test_prefix_entry_str():
    entry = PrefixEntry(prefix="refactor", count=4)
    assert str(entry) == "refactor: 4"
