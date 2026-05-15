"""Tests for gitlog_digest.commit_graph."""
from datetime import datetime, timezone
from typing import List

import pytest

from gitlog_digest.commit_graph import (
    CommitGraph,
    GraphRow,
    build_commit_graph,
    format_commit_graph,
)
from gitlog_digest.git_reader import GitCommit


def _c(day: str, author: str = "alice") -> GitCommit:
    dt = datetime.fromisoformat(f"{day}T10:00:00").replace(tzinfo=timezone.utc)
    return GitCommit(sha="abc1234", author=author, date=dt, message="msg")


def test_empty_commits_returns_empty_graph():
    graph = build_commit_graph([])
    assert graph.total == 0
    assert graph.rows == []
    assert graph.peak_day is None
    assert graph.max_count == 0


def test_single_commit_creates_one_row():
    graph = build_commit_graph([_c("2024-03-04")])
    assert len(graph.rows) == 1
    assert graph.rows[0].count == 1
    assert graph.total == 1


def test_multiple_commits_same_day_grouped():
    commits = [_c("2024-03-04"), _c("2024-03-04"), _c("2024-03-04")]
    graph = build_commit_graph(commits)
    assert len(graph.rows) == 1
    assert graph.rows[0].count == 3


def test_commits_across_days_sorted():
    commits = [_c("2024-03-06"), _c("2024-03-04"), _c("2024-03-05")]
    graph = build_commit_graph(commits)
    days = [r.day.isoformat() for r in graph.rows]
    assert days == ["2024-03-04", "2024-03-05", "2024-03-06"]


def test_peak_day_is_busiest():
    commits = [_c("2024-03-04"), _c("2024-03-05"), _c("2024-03-05")]
    graph = build_commit_graph(commits)
    assert graph.peak_day.isoformat() == "2024-03-05"


def test_max_count_reflects_busiest_day():
    commits = [_c("2024-03-04")] * 2 + [_c("2024-03-05")] * 5
    graph = build_commit_graph(commits)
    assert graph.max_count == 5


def test_graph_row_bar_full():
    row = GraphRow(day=None, count=20)
    assert row.bar(20) == "█" * 20


def test_graph_row_bar_half():
    row = GraphRow(day=None, count=10)
    bar = row.bar(20)
    assert len(bar) == 10


def test_graph_row_bar_zero_max():
    row = GraphRow(day=None, count=0)
    assert row.bar(0) == ""


def test_format_commit_graph_contains_title():
    graph = build_commit_graph([_c("2024-03-04")])
    output = format_commit_graph(graph, title="My Graph")
    assert "My Graph" in output


def test_format_commit_graph_empty_message():
    graph = build_commit_graph([])
    output = format_commit_graph(graph)
    assert "no commits" in output


def test_format_commit_graph_shows_total():
    commits = [_c("2024-03-04"), _c("2024-03-05")]
    graph = build_commit_graph(commits)
    output = format_commit_graph(graph)
    assert "Total: 2" in output
