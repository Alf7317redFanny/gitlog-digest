"""Tests for gitlog_digest.commit_pattern."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from gitlog_digest.commit_pattern import (
    CommitPatternReport,
    PatternEntry,
    _commit_type,
    build_pattern_report,
)
from gitlog_digest.git_reader import GitCommit


def _c(subject: str, ts: str = "2024-03-04T10:00:00+00:00") -> GitCommit:
    return GitCommit(
        sha="abc1234",
        subject=subject,
        author="Alice",
        date=datetime.fromisoformat(ts),
    )


# --- _commit_type ---

def test_commit_type_feat():
    assert _commit_type("feat: add login") == "feat"


def test_commit_type_fix_with_scope():
    assert _commit_type("fix(auth): handle null token") == "fix"


def test_commit_type_unknown_returns_none():
    assert _commit_type("initial commit") is None


def test_commit_type_case_insensitive():
    assert _commit_type("FEAT: something") == "feat"


# --- build_pattern_report ---

def test_empty_commits_returns_empty_report():
    report = build_pattern_report([])
    assert report.total == 0
    assert report.top_type is None
    assert len(report) == 0


def test_single_typed_commit():
    report = build_pattern_report([_c("feat: new thing")])
    assert report.total == 1
    assert report.top_type == "feat"


def test_untyped_commits_ignored():
    report = build_pattern_report([_c("wip stuff"), _c("misc changes")])
    assert report.total == 0


def test_multiple_types_sorted_by_count():
    commits = [
        _c("fix: bug"),
        _c("fix: another bug"),
        _c("feat: new feature"),
    ]
    report = build_pattern_report(commits)
    entries = report.sorted_entries()
    assert entries[0].commit_type == "fix"
    assert entries[0].count == 2
    assert entries[1].commit_type == "feat"
    assert entries[1].count == 1


def test_top_type_is_most_frequent():
    commits = [_c("chore: lint")] * 5 + [_c("feat: x")] * 2
    report = build_pattern_report(commits)
    assert report.top_type == "chore"


def test_peak_day_returned():
    commits = [
        _c("fix: a", "2024-03-04T09:00:00+00:00"),
        _c("fix: b", "2024-03-04T11:00:00+00:00"),
        _c("fix: c", "2024-03-05T08:00:00+00:00"),
    ]
    report = build_pattern_report(commits)
    from datetime import date
    assert report._entries["fix"].peak_day == date(2024, 3, 4)


def test_len_counts_distinct_types():
    commits = [_c("feat: x"), _c("fix: y"), _c("docs: z")]
    report = build_pattern_report(commits)
    assert len(report) == 3
