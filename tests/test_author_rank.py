"""Tests for gitlog_digest.author_rank."""

import datetime
import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.author_rank import (
    build_author_rank,
    format_author_rank_report,
    AuthorRankReport,
)


def _c(author: str, sha: str = "abc1234") -> GitCommit:
    return GitCommit(
        sha=sha,
        author=author,
        date=datetime.date(2024, 6, 3),
        subject="some commit",
    )


def test_empty_input_returns_empty_report():
    report = build_author_rank({})
    assert len(report) == 0
    assert report.entries == []


def test_single_author_single_repo():
    commits = {"repo-a": [_c("Alice"), _c("Alice", "def5678")]}
    report = build_author_rank(commits)
    assert len(report) == 1
    assert report.entries[0].author == "Alice"
    assert report.entries[0].commit_count == 2
    assert report.entries[0].repos == ["repo-a"]


def test_multiple_authors_sorted_by_count():
    commits = {
        "repo-a": [
            _c("Alice", "aaa"),
            _c("Alice", "bbb"),
            _c("Bob", "ccc"),
        ]
    }
    report = build_author_rank(commits)
    assert report.entries[0].author == "Alice"
    assert report.entries[1].author == "Bob"


def test_author_across_multiple_repos():
    commits = {
        "repo-a": [_c("Alice", "aaa")],
        "repo-b": [_c("Alice", "bbb")],
    }
    report = build_author_rank(commits)
    entry = report.entries[0]
    assert entry.author == "Alice"
    assert entry.commit_count == 2
    assert set(entry.repos) == {"repo-a", "repo-b"}


def test_top_n_limits_results():
    authors = [f"Author{i}" for i in range(10)]
    commits = {"repo": [_c(a, f"sha{i}") for i, a in enumerate(authors)]}
    report = build_author_rank(commits)
    assert len(report.top(3)) == 3


def test_format_report_contains_author_name():
    commits = {"repo-a": [_c("Charlie", "xyz")]}
    report = build_author_rank(commits)
    text = format_author_rank_report(report)
    assert "Charlie" in text
    assert "1" in text


def test_format_report_empty():
    report = AuthorRankReport(entries=[])
    text = format_author_rank_report(report)
    assert "No author data" in text


def test_str_on_entry():
    commits = {"my-repo": [_c("Dana", "111"), _c("Dana", "222")]}
    report = build_author_rank(commits)
    s = str(report.entries[0])
    assert "Dana" in s
    assert "my-repo" in s
    assert "2" in s
