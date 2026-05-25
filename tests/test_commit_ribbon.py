from datetime import datetime, timezone

import pytest

from gitlog_digest.commit_ribbon import CommitRibbonReport, RibbonDay
from gitlog_digest.git_reader import GitCommit


def _c(sha: str, author: str, date_str: str, subject: str = "msg") -> GitCommit:
    dt = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    return GitCommit(sha=sha, author=author, date=dt, subject=subject, files=[])


def test_empty_commits_returns_empty_report():
    r = CommitRibbonReport()
    r.add_commits([])
    assert r.total == 0
    assert r.days == []
    assert r.peak_day is None


def test_single_day_single_commit():
    r = CommitRibbonReport()
    r.add_commits([_c("a", "Alice", "2024-03-04T10:00:00")])
    assert r.total == 1
    assert len(r.days) == 1
    assert r.days[0].count == 1
    assert r.days[0].delta == 0


def test_multiple_commits_same_day_grouped():
    r = CommitRibbonReport()
    commits = [
        _c("a", "Alice", "2024-03-04T09:00:00"),
        _c("b", "Bob", "2024-03-04T11:00:00"),
        _c("c", "Alice", "2024-03-04T14:00:00"),
    ]
    r.add_commits(commits)
    assert len(r.days) == 1
    assert r.days[0].count == 3


def test_delta_computed_between_days():
    r = CommitRibbonReport()
    commits = [
        _c("a", "Alice", "2024-03-04T10:00:00"),
        _c("b", "Alice", "2024-03-05T10:00:00"),
        _c("c", "Alice", "2024-03-05T11:00:00"),
        _c("d", "Alice", "2024-03-06T10:00:00"),
    ]
    r.add_commits(commits)
    days = r.days
    assert days[0].delta == 0   # first day baseline
    assert days[1].delta == 1   # 2 - 1
    assert days[2].delta == -1  # 1 - 2


def test_trend_accelerating():
    r = CommitRibbonReport()
    commits = [
        _c("a", "A", "2024-03-04T10:00:00"),
        _c("b", "A", "2024-03-05T10:00:00"),
        _c("c", "A", "2024-03-05T11:00:00"),
        _c("d", "A", "2024-03-06T10:00:00"),
        _c("e", "A", "2024-03-06T11:00:00"),
        _c("f", "A", "2024-03-06T12:00:00"),
    ]
    r.add_commits(commits)
    assert r.trend == "accelerating"


def test_trend_decelerating():
    r = CommitRibbonReport()
    commits = [
        _c("a", "A", "2024-03-04T10:00:00"),
        _c("b", "A", "2024-03-04T11:00:00"),
        _c("c", "A", "2024-03-04T12:00:00"),
        _c("d", "A", "2024-03-05T10:00:00"),
        _c("e", "A", "2024-03-05T11:00:00"),
        _c("f", "A", "2024-03-06T10:00:00"),
    ]
    r.add_commits(commits)
    assert r.trend == "decelerating"


def test_trend_steady_single_day():
    r = CommitRibbonReport()
    r.add_commits([_c("a", "A", "2024-03-04T10:00:00")])
    assert r.trend == "steady"


def test_peak_day_is_highest_count_day():
    r = CommitRibbonReport()
    commits = [
        _c("a", "A", "2024-03-04T10:00:00"),
        _c("b", "A", "2024-03-05T10:00:00"),
        _c("c", "A", "2024-03-05T11:00:00"),
    ]
    r.add_commits(commits)
    from datetime import date
    assert r.peak_day == date(2024, 3, 5)


def test_format_report_contains_trend():
    r = CommitRibbonReport()
    r.add_commits([_c("a", "A", "2024-03-04T10:00:00")])
    text = r.format_report()
    assert "Trend:" in text
    assert "steady" in text


def test_format_report_empty():
    r = CommitRibbonReport()
    r.add_commits([])
    assert r.format_report() == "No commits."
