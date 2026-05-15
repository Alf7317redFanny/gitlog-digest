"""Tests for repeat_authors module."""
from datetime import datetime

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.repeat_authors import (
    RepeatAuthorReport,
    compare_author_sets,
    format_repeat_author_report,
    repeat_author_dict,
)


def _c(author: str) -> GitCommit:
    return GitCommit(
        sha="abc1234",
        author=author,
        date=datetime(2024, 1, 15, 10, 0, 0),
        message="chore: something",
    )


def test_all_returning():
    prev = [_c("alice"), _c("bob")]
    curr = [_c("alice"), _c("bob")]
    report = compare_author_sets(prev, curr)
    assert sorted(report.returning) == ["alice", "bob"]
    assert report.new_this_week == []
    assert report.dropped_off == []


def test_all_new():
    prev = [_c("alice")]
    curr = [_c("carol")]
    report = compare_author_sets(prev, curr)
    assert report.returning == []
    assert report.new_this_week == ["carol"]
    assert report.dropped_off == ["alice"]


def test_mixed_returning_new_dropped():
    prev = [_c("alice"), _c("bob")]
    curr = [_c("alice"), _c("carol")]
    report = compare_author_sets(prev, curr)
    assert report.returning == ["alice"]
    assert report.new_this_week == ["carol"]
    assert report.dropped_off == ["bob"]


def test_empty_previous():
    prev = []
    curr = [_c("alice")]
    report = compare_author_sets(prev, curr)
    assert report.returning == []
    assert report.new_this_week == ["alice"]
    assert report.dropped_off == []


def test_empty_current():
    prev = [_c("alice")]
    curr = []
    report = compare_author_sets(prev, curr)
    assert report.returning == []
    assert report.new_this_week == []
    assert report.dropped_off == ["alice"]


def test_counts():
    report = RepeatAuthorReport(
        returning=["alice"],
        new_this_week=["bob", "carol"],
        dropped_off=[],
    )
    assert report.returning_count == 1
    assert report.new_count == 2
    assert report.dropped_count == 0


def test_format_includes_sections():
    prev = [_c("alice"), _c("bob")]
    curr = [_c("alice"), _c("carol")]
    report = compare_author_sets(prev, curr)
    text = format_repeat_author_report(report)
    assert "## Author Retention" in text
    assert "Returning" in text
    assert "alice" in text
    assert "carol" in text
    assert "bob" in text


def test_format_empty_sections_show_dash():
    report = RepeatAuthorReport()
    text = format_repeat_author_report(report)
    assert "—" in text


def test_dict_keys():
    report = RepeatAuthorReport(returning=["alice"], new_this_week=["bob"], dropped_off=[])
    d = repeat_author_dict(report)
    assert set(d.keys()) == {
        "returning", "new_this_week", "dropped_off",
        "returning_count", "new_count", "dropped_count",
    }
    assert d["returning"] == ["alice"]
    assert d["new_count"] == 1
