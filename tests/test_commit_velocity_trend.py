"""Tests for commit_velocity_trend module."""
from datetime import datetime, timezone

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_velocity_trend import (
    CommitVelocityTrendReport,
    VelocityTrendEntry,
    build_velocity_trend,
    format_velocity_trend_report,
)


def _c(author: str, subject: str = "chore: work") -> GitCommit:
    return GitCommit(
        sha="abc1234",
        author=author,
        date=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
        subject=subject,
        files_changed=[],
    )


def test_empty_commits_returns_empty_report():
    report = build_velocity_trend([])
    assert len(report) == 0
    assert report.entries() == []


def test_single_week_single_author():
    report = build_velocity_trend([[_c("alice"), _c("alice")]])
    assert len(report) == 1
    entry = report.entries()[0]
    assert entry.author == "alice"
    assert entry.weekly_counts == [2]


def test_trend_up_when_count_increases():
    report = build_velocity_trend([[_c("alice")], [_c("alice"), _c("alice")]])
    entry = report.entries()[0]
    assert entry.trend == "up"


def test_trend_down_when_count_decreases():
    report = build_velocity_trend(
        [[_c("alice"), _c("alice"), _c("alice")], [_c("alice")]]
    )
    entry = report.entries()[0]
    assert entry.trend == "down"


def test_trend_stable_when_counts_equal():
    report = build_velocity_trend([[_c("alice"), _c("alice")], [_c("alice"), _c("alice")]])
    entry = report.entries()[0]
    assert entry.trend == "stable"


def test_trend_stable_for_single_week():
    entry = VelocityTrendEntry(author="bob", weekly_counts=[5])
    assert entry.trend == "stable"


def test_author_gets_zero_for_absent_week():
    report = build_velocity_trend([[_c("alice")], [_c("bob")]])
    alice = next(e for e in report.entries() if e.author == "alice")
    assert alice.weekly_counts == [1, 0]


def test_new_author_in_later_week():
    report = build_velocity_trend([[_c("alice")], [_c("alice"), _c("bob")]])
    bob = next(e for e in report.entries() if e.author == "bob")
    assert bob.weekly_counts == [1]


def test_top_n_limits_results():
    authors = [f"author{i}" for i in range(10)]
    week = [_c(a) for a in authors]
    report = build_velocity_trend([week])
    assert len(report.top(3)) == 3


def test_format_report_contains_author_name():
    report = build_velocity_trend([[_c("alice"), _c("alice")]])
    text = format_velocity_trend_report(report)
    assert "alice" in text


def test_format_empty_report_returns_no_data_message():
    report = build_velocity_trend([])
    text = format_velocity_trend_report(report)
    assert "no data" in text


def test_str_representation_contains_arrow():
    entry = VelocityTrendEntry(author="dev", weekly_counts=[1, 3])
    assert "↑" in str(entry)
