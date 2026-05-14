"""Tests for template_renderer module."""

from __future__ import annotations

from datetime import date

import pytest

from gitlog_digest.digest import Digest, RepoSummary
from gitlog_digest.git_reader import GitCommit
from gitlog_digest.stats import CommitStats, compute_stats
from gitlog_digest.template_renderer import TemplateConfig, render_digest
from gitlog_digest.week_range import WeekRange


def _make_week() -> WeekRange:
    return WeekRange.containing(date(2024, 3, 11))


def _make_commit(author: str, day: date) -> GitCommit:
    return GitCommit(
        sha="abc1234",
        author=author,
        date=day,
        message="some work",
    )


def _make_digest_with_stats():
    week = _make_week()
    commits = [
        _make_commit("alice", date(2024, 3, 11)),
        _make_commit("alice", date(2024, 3, 12)),
        _make_commit("bob", date(2024, 3, 11)),
    ]
    summary = RepoSummary(repo="myrepo", commits=commits)
    digest = Digest(week=week, repos={"myrepo": summary})
    stats = compute_stats(commits)
    return digest, {"myrepo": stats}


def test_render_contains_week_label():
    digest, stats_map = _make_digest_with_stats()
    output = render_digest(digest, stats_map)
    assert "2024-W11" in output or "Mar" in output or digest.week.label() in output


def test_render_contains_repo_name():
    digest, stats_map = _make_digest_with_stats()
    output = render_digest(digest, stats_map)
    assert "myrepo" in output


def test_render_shows_commit_count():
    digest, stats_map = _make_digest_with_stats()
    output = render_digest(digest, stats_map)
    assert "3" in output


def test_render_shows_top_author():
    digest, stats_map = _make_digest_with_stats()
    output = render_digest(digest, stats_map)
    assert "alice" in output


def test_render_no_activity_message_when_empty():
    week = _make_week()
    summary = RepoSummary(repo="emptyrepo", commits=[])
    digest = Digest(week=week, repos={"emptyrepo": summary})
    stats = compute_stats([])
    output = render_digest(digest, {"emptyrepo": stats})
    assert "No commits" in output or "no commits" in output.lower()


def test_render_missing_stats_shows_no_activity():
    week = _make_week()
    summary = RepoSummary(repo="ghostrepo", commits=[])
    digest = Digest(week=week, repos={"ghostrepo": summary})
    output = render_digest(digest, {})
    assert "ghostrepo" in output


def test_custom_template_config():
    digest, stats_map = _make_digest_with_stats()
    cfg = TemplateConfig(
        header_template="WEEK:{week_label}\n{repo_sections}\nTOTAL:{total_commits}",
        repo_template="REPO:{repo_name} COUNT:{commit_count} TOP:{top_author} DAY:{most_active_day} AUTH:{authors}",
    )
    output = render_digest(digest, stats_map, cfg=cfg)
    assert output.startswith("WEEK:")
    assert "REPO:myrepo" in output
