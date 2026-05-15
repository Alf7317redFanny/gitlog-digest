"""Tests for gitlog_digest.message_length."""
from datetime import datetime

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.message_length import (
    MessageLengthReport,
    build_message_length_report,
    format_message_length_report,
    message_length_report_dict,
)


def _c(subject: str) -> GitCommit:
    return GitCommit(
        sha="abc1234",
        subject=subject,
        author="Dev",
        date=datetime(2024, 1, 15, 10, 0, 0),
    )


def test_empty_commits_returns_empty_report():
    report = build_message_length_report([])
    assert report.total == 0
    assert report.average == 0.0
    assert report.shortest == 0
    assert report.longest == 0
    assert report.over_72 == 0


def test_single_commit_length():
    report = build_message_length_report([_c("fix: correct typo")])
    assert report.total == 1
    assert report.shortest == report.longest == len("fix: correct typo")


def test_average_computed_correctly():
    commits = [_c("ab"), _c("abcd"), _c("abcdef")]  # 2, 4, 6
    report = build_message_length_report(commits)
    assert report.average == 4.0


def test_median_computed_correctly():
    commits = [_c("a"), _c("abc"), _c("abcde")]  # 1, 3, 5
    report = build_message_length_report(commits)
    assert report.median_length == 3.0


def test_over_72_counts_long_messages():
    short = _c("x" * 50)
    exact = _c("x" * 72)
    over = _c("x" * 80)
    report = build_message_length_report([short, exact, over])
    assert report.over_72 == 1


def test_over_72_none_exceed():
    commits = [_c("short message"), _c("another short one")]
    report = build_message_length_report(commits)
    assert report.over_72 == 0


def test_len_matches_total():
    report = build_message_length_report([_c("a"), _c("bb"), _c("ccc")])
    assert len(report) == 3


def test_format_report_contains_key_fields():
    report = build_message_length_report([_c("fix: something"), _c("x" * 80)])
    text = format_message_length_report(report)
    assert "Average" in text
    assert "Over 72" in text
    assert "Total" in text


def test_format_empty_report():
    report = build_message_length_report([])
    text = format_message_length_report(report)
    assert "no commits" in text


def test_report_dict_keys():
    report = build_message_length_report([_c("feat: add widget")])
    d = message_length_report_dict(report)
    assert set(d.keys()) == {"total", "average", "median", "shortest", "longest", "over_72"}


def test_report_dict_values_match_report():
    commits = [_c("fix: bug"), _c("x" * 100)]
    report = build_message_length_report(commits)
    d = message_length_report_dict(report)
    assert d["total"] == report.total
    assert d["over_72"] == report.over_72
    assert d["longest"] == report.longest
