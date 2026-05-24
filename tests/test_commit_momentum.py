"""Tests for commit_momentum.py"""
import pytest
from datetime import datetime

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_momentum import (
    MomentumEntry,
    CommitMomentumReport,
    build_momentum_report,
    format_momentum_report,
)


def _c(author: str, subject: str = "chore: update") -> GitCommit:
    return GitCommit(
        sha="abc1234",
        short_sha="abc1234"[:7],
        author=author,
        date=datetime(2024, 1, 15, 10, 0),
        subject=subject,
        files_changed=[],
        insertions=0,
        deletions=0,
        branch="main",
    )


def test_empty_commits_returns_empty_report():
    report = build_momentum_report([], [])
    assert len(report) == 0
    assert report.total_delta == 0
    assert report.overall_trend == "flat"


def test_single_author_increase():
    current = [_c("alice"), _c("alice"), _c("alice")]
    previous = [_c("alice")]
    report = build_momentum_report(current, previous)
    entries = report.entries()
    assert len(entries) == 1
    assert entries[0].delta == 2
    assert entries[0].trend == "up"


def test_single_author_decrease():
    current = [_c("bob")]
    previous = [_c("bob"), _c("bob"), _c("bob")]
    report = build_momentum_report(current, previous)
    entry = report.entries()[0]
    assert entry.delta == -2
    assert entry.trend == "down"


def test_flat_trend_when_counts_equal():
    current = [_c("carol"), _c("carol")]
    previous = [_c("carol"), _c("carol")]
    report = build_momentum_report(current, previous)
    entry = report.entries()[0]
    assert entry.trend == "flat"
    assert entry.delta == 0


def test_new_author_has_infinite_like_ratio():
    current = [_c("dave")]
    previous = []
    report = build_momentum_report(current, previous)
    entry = report.entries()[0]
    assert entry.previous_count == 0
    assert entry.ratio == float(entry.current_count)


def test_dropped_author_in_report():
    current = []
    previous = [_c("eve"), _c("eve")]
    report = build_momentum_report(current, previous)
    entry = report.entries()[0]
    assert entry.author == "eve"
    assert entry.current_count == 0
    assert entry.delta == -2


def test_entries_sorted_by_delta_descending():
    current = [_c("a"), _c("a"), _c("a"), _c("b")]
    previous = [_c("a"), _c("b"), _c("b"), _c("b")]
    report = build_momentum_report(current, previous)
    deltas = [e.delta for e in report.entries()]
    assert deltas == sorted(deltas, reverse=True)


def test_overall_trend_up_when_positive_delta():
    current = [_c("x"), _c("x"), _c("x")]
    previous = [_c("x")]
    report = build_momentum_report(current, previous)
    assert report.overall_trend == "up"
    assert report.total_delta == 2


def test_format_momentum_report_non_empty():
    current = [_c("alice"), _c("alice")]
    previous = [_c("alice")]
    report = build_momentum_report(current, previous)
    text = format_momentum_report(report)
    assert "alice" in text
    assert "up" in text


def test_format_momentum_report_empty():
    report = CommitMomentumReport()
    text = format_momentum_report(report)
    assert "No momentum" in text


def test_momentum_entry_str_positive_delta():
    entry = MomentumEntry(author="zara", current_count=5, previous_count=2)
    s = str(entry)
    assert "zara" in s
    assert "+3" in s
    assert "up" in s
