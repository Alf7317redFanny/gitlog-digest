"""Tests for gitlog_digest.stats."""

import pytest
from gitlog_digest.git_reader import GitCommit
from gitlog_digest.stats import CommitStats, compute_stats, most_active_day


def c(sha, author, date):
    return GitCommit(sha=sha, author=author, date=date, subject="msg")


COMMITS = [
    c("a1", "Alice", "2024-01-15 10:00:00"),
    c("a2", "Alice", "2024-01-15 14:00:00"),
    c("b1", "Bob",   "2024-01-16 09:00:00"),
    c("a3", "Alice", "2024-01-17 11:00:00"),
    c("c1", "Carol", "2024-01-16 16:00:00"),
]


def test_total_count():
    stats = compute_stats(COMMITS)
    assert stats.total == 5


def test_by_author():
    stats = compute_stats(COMMITS)
    assert stats.by_author["Alice"] == 3
    assert stats.by_author["Bob"] == 1
    assert stats.by_author["Carol"] == 1


def test_unique_authors():
    stats = compute_stats(COMMITS)
    assert stats.unique_authors == 3


def test_top_author():
    stats = compute_stats(COMMITS)
    assert stats.top_author == "Alice"


def test_by_date():
    stats = compute_stats(COMMITS)
    assert stats.by_date["2024-01-15"] == 2
    assert stats.by_date["2024-01-16"] == 2
    assert stats.by_date["2024-01-17"] == 1


def test_most_active_day():
    stats = compute_stats(COMMITS)
    # 2024-01-15 and 2024-01-16 are tied; max picks deterministically
    assert most_active_day(stats) in {"2024-01-15", "2024-01-16"}


def test_empty_commits():
    stats = compute_stats([])
    assert stats.total == 0
    assert stats.by_author == {}
    assert stats.top_author == ""
    assert stats.unique_authors == 0


def test_most_active_day_empty():
    assert most_active_day(CommitStats()) == ""
