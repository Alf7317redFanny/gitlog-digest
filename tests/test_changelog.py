"""Tests for gitlog_digest.changelog."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from gitlog_digest.changelog import (
    build_changelog,
    format_changelog,
    _group_by_day,
)
from gitlog_digest.git_reader import GitCommit


def _commit(sha: str, subject: str, day: int, hour: int = 10) -> GitCommit:
    dt = datetime(2024, 6, day, hour, 0, 0, tzinfo=timezone.utc)
    return GitCommit(sha=sha, subject=subject, author="Alice", date=dt)


def _make_digest(commits_per_repo):
    """Build a minimal Digest-like mock."""
    digest = MagicMock()
    digest.week.label = "Week of 2024-06-17"
    summaries = []
    for repo_name, commits in commits_per_repo.items():
        s = MagicMock()
        s.repo_name = repo_name
        s.commits = commits
        summaries.append(s)
    digest.repos = summaries
    return digest


# --- _group_by_day ---

def test_group_by_day_single_day():
    commits = [_commit("aaa", "fix bug", 17), _commit("bbb", "add test", 17)]
    groups = _group_by_day(commits)
    assert len(groups) == 1
    assert len(groups[0]) == 2


def test_group_by_day_multiple_days():
    commits = [
        _commit("aaa", "day one", 17),
        _commit("bbb", "day two", 18),
        _commit("ccc", "also day one", 17),
    ]
    groups = _group_by_day(commits)
    assert len(groups) == 2
    assert groups[0].day.day == 17
    assert len(groups[0]) == 2
    assert groups[1].day.day == 18


def test_group_by_day_empty():
    assert _group_by_day([]) == []


# --- build_changelog ---

def test_build_changelog_week_label():
    digest = _make_digest({})
    cl = build_changelog(digest)
    assert cl.week_label == "Week of 2024-06-17"


def test_build_changelog_repo_names():
    digest = _make_digest({"repo-a": [], "repo-b": []})
    cl = build_changelog(digest)
    names = [r.repo_name for r in cl.repos]
    assert names == ["repo-a", "repo-b"]


def test_build_changelog_total_commits():
    commits = [_commit("x", "s", 17), _commit("y", "t", 18)]
    digest = _make_digest({"my-repo": commits})
    cl = build_changelog(digest)
    assert cl.total_commits == 2
    assert cl.repos[0].total_commits == 2


# --- format_changelog ---

def test_format_changelog_contains_week_label():
    digest = _make_digest({"proj": [_commit("abc", "init", 17)]})
    cl = build_changelog(digest)
    output = format_changelog(cl)
    assert "Week of 2024-06-17" in output


def test_format_changelog_contains_repo_and_sha():
    digest = _make_digest({"my-proj": [_commit("deadbeef", "cool feature", 17)]})
    cl = build_changelog(digest)
    output = format_changelog(cl)
    assert "my-proj" in output
    assert "deadbeef" in output
    assert "cool feature" in output


def test_format_changelog_empty_repos():
    digest = _make_digest({})
    cl = build_changelog(digest)
    output = format_changelog(cl)
    assert "Changelog" in output
