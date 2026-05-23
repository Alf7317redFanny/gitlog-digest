"""Tests for commit_timezone module."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from gitlog_digest.commit_timezone import (
    CommitTimezoneReport,
    build_timezone_report,
    format_timezone_report,
    _offset_label,
)
from gitlog_digest.git_reader import GitCommit


def _c(offset_hours: float = 0, subject: str = "chore: test") -> GitCommit:
    tz = timezone(timedelta(hours=offset_hours))
    return GitCommit(
        sha="abc1234",
        author="Dev",
        author_date=datetime(2024, 6, 3, 10, 0, 0, tzinfo=tz),
        subject=subject,
        files_changed=[],
        insertions=0,
        deletions=0,
        branch="main",
    )


def test_offset_label_positive_whole():
    assert _offset_label(60) == "UTC+01"


def test_offset_label_negative():
    assert _offset_label(-300) == "UTC-05"


def test_offset_label_with_minutes():
    assert _offset_label(330) == "UTC+05:30"


def test_offset_label_utc():
    assert _offset_label(0) == "UTC+00"


def test_empty_commits_returns_empty_report():
    report = build_timezone_report([])
    assert report.total == 0
    assert len(report) == 0
    assert report.top() == []


def test_single_commit_counted_correctly():
    report = build_timezone_report([_c(offset_hours=2)])
    assert report.total == 1
    assert len(report) == 1
    entry = report.entry_for(120)
    assert entry is not None
    assert entry.count == 1
    assert entry.label == "UTC+02"


def test_multiple_commits_same_offset():
    commits = [_c(offset_hours=1), _c(offset_hours=1), _c(offset_hours=1)]
    report = build_timezone_report(commits)
    assert report.total == 3
    assert len(report) == 1
    assert report.entry_for(60).count == 3


def test_commits_across_offsets():
    commits = [_c(0), _c(1), _c(2), _c(1)]
    report = build_timezone_report(commits)
    assert report.total == 4
    assert len(report) == 3


def test_top_returns_sorted_by_count():
    commits = [_c(0), _c(1), _c(1), _c(2), _c(2), _c(2)]
    report = build_timezone_report(commits)
    top = report.top(2)
    assert top[0].offset_minutes == 120
    assert top[1].offset_minutes == 60


def test_top_n_larger_than_entries_returns_all():
    report = build_timezone_report([_c(0), _c(1)])
    assert len(report.top(100)) == 2


def test_offsets_property_sorted():
    commits = [_c(3), _c(-1), _c(0)]
    report = build_timezone_report(commits)
    assert report.offsets == [-60, 0, 180]


def test_format_timezone_report_empty():
    report = build_timezone_report([])
    text = format_timezone_report(report)
    assert "no commits" in text


def test_format_timezone_report_contains_label():
    report = build_timezone_report([_c(5.5)])
    text = format_timezone_report(report)
    assert "UTC+05:30" in text


def test_entry_str_singular():
    report = build_timezone_report([_c(0)])
    entry = report.entry_for(0)
    assert str(entry) == "UTC+00: 1 commit"


def test_entry_str_plural():
    report = build_timezone_report([_c(0), _c(0)])
    entry = report.entry_for(0)
    assert str(entry) == "UTC+00: 2 commits"
