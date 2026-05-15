"""Tests for commit_sentiment module."""

import pytest
from datetime import datetime

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_sentiment import (
    build_sentiment_report,
    format_sentiment_report,
    _classify,
)


def _c(subject: str, author: str = "dev") -> GitCommit:
    return GitCommit(
        sha="abc1234",
        short_sha="abc1234"[:7],
        subject=subject,
        author=author,
        date=datetime(2024, 1, 15, 10, 0, 0),
        files_changed=[],
        insertions=0,
        deletions=0,
    )


def test_classify_positive():
    assert _classify("add new login feature") == "positive"


def test_classify_negative():
    assert _classify("revert broken deployment") == "negative"


def test_classify_neutral():
    assert _classify("update docs for v2") == "neutral"


def test_classify_positive_beats_negative():
    # 2 positive words, 1 negative
    assert _classify("fix and improve the hack") == "positive"


def test_empty_commits_returns_empty_report():
    report = build_sentiment_report([])
    assert report.total == 0
    assert report.positive_ratio == 0.0
    assert report.negative_ratio == 0.0


def test_single_positive_commit():
    report = build_sentiment_report([_c("add user authentication")])
    assert len(report.positive) == 1
    assert len(report.negative) == 0
    assert report.positive_ratio == 1.0


def test_single_negative_commit():
    report = build_sentiment_report([_c("revert last merge")])
    assert len(report.negative) == 1
    assert report.negative_ratio == 1.0


def test_mixed_commits():
    commits = [
        _c("fix login bug"),
        _c("revert broken pipeline"),
        _c("update readme"),
    ]
    report = build_sentiment_report(commits)
    assert report.total == 3
    assert len(report.positive) == 1
    assert len(report.negative) == 1
    assert len(report.neutral) == 1


def test_summary_dict_keys():
    report = build_sentiment_report([_c("add feature"), _c("revert change")])
    d = report.summary_dict()
    assert set(d.keys()) == {"positive", "negative", "neutral"}


def test_format_report_contains_labels():
    commits = [_c("add feature"), _c("revert change"), _c("update docs")]
    report = build_sentiment_report(commits)
    text = format_sentiment_report(report)
    assert "Positive" in text
    assert "Negative" in text
    assert "Neutral" in text


def test_format_report_empty():
    report = build_sentiment_report([])
    text = format_sentiment_report(report)
    assert "No commits" in text
