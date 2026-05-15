"""Tests for gitlog_digest.author_timeline."""

from datetime import datetime, date

import pytest

from gitlog_digest.author_timeline import (
    build_author_timeline,
    format_author_timeline,
    AuthorTimeline,
)
from gitlog_digest.git_reader import GitCommit


def _c(author: str, day: date) -> GitCommit:
    dt = datetime(day.year, day.month, day.day, 12, 0, 0)
    return GitCommit(sha="abc1234", author=author, date=dt, message="chore: test")


MON = date(2024, 1, 8)
TUE = date(2024, 1, 9)
WED = date(2024, 1, 10)


def test_empty_commits_returns_empty_timeline():
    tl = build_author_timeline([])
    assert tl.authors == []
    assert tl.all_dates == []


def test_single_commit_single_author():
    tl = build_author_timeline([_c("alice", MON)])
    assert tl.authors == ["alice"]
    assert tl.count_on("alice", MON) == 1


def test_multiple_commits_same_day_aggregated():
    commits = [_c("alice", MON), _c("alice", MON), _c("alice", MON)]
    tl = build_author_timeline(commits)
    assert tl.count_on("alice", MON) == 3


def test_multiple_authors_tracked_separately():
    commits = [_c("alice", MON), _c("bob", MON), _c("alice", TUE)]
    tl = build_author_timeline(commits)
    assert set(tl.authors) == {"alice", "bob"}
    assert tl.count_on("alice", MON) == 1
    assert tl.count_on("bob", MON) == 1
    assert tl.count_on("alice", TUE) == 1
    assert tl.count_on("bob", TUE) == 0


def test_all_dates_is_union_of_all_authors():
    commits = [_c("alice", MON), _c("bob", WED)]
    tl = build_author_timeline(commits)
    assert tl.all_dates == [MON, WED]


def test_dates_for_returns_only_active_days():
    commits = [_c("alice", MON), _c("alice", WED), _c("bob", TUE)]
    tl = build_author_timeline(commits)
    assert tl.dates_for("alice") == [MON, WED]
    assert tl.dates_for("bob") == [TUE]


def test_count_on_unknown_author_returns_zero():
    tl = build_author_timeline([_c("alice", MON)])
    assert tl.count_on("nobody", MON) == 0


def test_format_includes_author_name():
    tl = build_author_timeline([_c("alice", MON)])
    output = format_author_timeline(tl)
    assert "alice" in output


def test_format_empty_returns_message():
    tl = AuthorTimeline()
    assert format_author_timeline(tl) == "No commits found."


def test_format_includes_day_abbreviation():
    tl = build_author_timeline([_c("alice", MON)])
    output = format_author_timeline(tl)
    assert "Mon" in output
