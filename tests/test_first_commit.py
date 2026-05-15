"""Tests for gitlog_digest.first_commit."""
from datetime import datetime, timezone

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.first_commit import (
    AuthorDebut,
    DebutReport,
    build_debut_report,
    format_debut_report,
)


def _c(author: str, date_str: str, subject: str = "some work", sha: str = "abc1234") -> GitCommit:
    dt = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    return GitCommit(sha=sha, author=author, date=dt, subject=subject)


# ---------------------------------------------------------------------------
# DebutReport.add
# ---------------------------------------------------------------------------

def test_add_single_commit():
    report = DebutReport()
    report.add("repo-a", _c("Alice", "2024-03-04"))
    assert report.total == 1
    assert "Alice" in report.debuts


def test_add_keeps_earliest():
    report = DebutReport()
    report.add("repo-a", _c("Alice", "2024-03-06", sha="aaa"))
    report.add("repo-a", _c("Alice", "2024-03-04", sha="bbb"))
    assert report.debuts["Alice"].sha == "bbb"


def test_add_multiple_authors():
    report = DebutReport()
    report.add("repo-a", _c("Alice", "2024-03-04"))
    report.add("repo-a", _c("Bob", "2024-03-05"))
    assert report.total == 2


def test_new_contributors_sorted_by_date():
    report = DebutReport()
    report.add("repo-a", _c("Bob", "2024-03-05"))
    report.add("repo-a", _c("Alice", "2024-03-04"))
    names = [d.author for d in report.new_contributors]
    assert names == ["Alice", "Bob"]


# ---------------------------------------------------------------------------
# build_debut_report
# ---------------------------------------------------------------------------

def test_build_debut_report_basic():
    commits = {"repo-a": [_c("Alice", "2024-03-04"), _c("Bob", "2024-03-05")]}
    report = build_debut_report(commits)
    assert report.total == 2


def test_build_debut_excludes_known_authors():
    commits = {"repo-a": [_c("Alice", "2024-03-04"), _c("Bob", "2024-03-05")]}
    report = build_debut_report(commits, known_authors=["Alice"])
    assert report.total == 1
    assert "Bob" in report.debuts


def test_build_debut_known_authors_case_insensitive():
    commits = {"repo-a": [_c("Alice", "2024-03-04")]}
    report = build_debut_report(commits, known_authors=["alice"])
    assert report.total == 0


def test_build_debut_multi_repo():
    commits = {
        "repo-a": [_c("Alice", "2024-03-06", sha="a1")],
        "repo-b": [_c("Alice", "2024-03-04", sha="b1"), _c("Carol", "2024-03-05", sha="c1")],
    }
    report = build_debut_report(commits)
    assert report.total == 2
    assert report.debuts["Alice"].sha == "b1"
    assert report.debuts["Alice"].repo == "repo-b"


# ---------------------------------------------------------------------------
# format_debut_report
# ---------------------------------------------------------------------------

def test_format_empty_report():
    report = DebutReport()
    text = format_debut_report(report)
    assert "No new contributors" in text


def test_format_nonempty_report():
    report = DebutReport()
    report.add("repo-a", _c("Alice", "2024-03-04", subject="init project"))
    text = format_debut_report(report)
    assert "Alice" in text
    assert "repo-a" in text
    assert "init project" in text


def test_author_debut_str():
    debut = AuthorDebut(
        author="Alice",
        sha="deadbeef",
        subject="hello world",
        date=datetime(2024, 3, 4, tzinfo=timezone.utc),
        repo="my-repo",
    )
    s = str(debut)
    assert "Alice" in s
    assert "my-repo" in s
    assert "2024-03-04" in s
    assert "deadbee" in s
