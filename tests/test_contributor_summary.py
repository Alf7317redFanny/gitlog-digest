"""Tests for contributor_summary module."""

import pytest
from datetime import datetime
from gitlog_digest.git_reader import GitCommit
from gitlog_digest.contributor_summary import (
    build_contributor_summary,
    format_contributor_summary,
    ContributorSummary,
)


def _c(author: str, subject: str = "some change") -> GitCommit:
    return GitCommit(
        sha="abc1234",
        author=author,
        date=datetime(2024, 6, 3, 10, 0, 0),
        subject=subject,
    )


def test_empty_input_returns_empty_summary():
    summary = build_contributor_summary({})
    assert summary.total_contributors == 0
    assert summary.top_contributor() is None


def test_single_repo_single_author():
    commits = {"repo-a": [_c("alice"), _c("alice")]}
    summary = build_contributor_summary(commits)
    assert summary.total_contributors == 1
    assert summary.entries["alice"].commit_count == 2
    assert "repo-a" in summary.entries["alice"].repos


def test_multiple_authors_same_repo():
    commits = {"repo-a": [_c("alice"), _c("bob"), _c("alice")]}
    summary = build_contributor_summary(commits)
    assert summary.total_contributors == 2
    assert summary.entries["alice"].commit_count == 2
    assert summary.entries["bob"].commit_count == 1


def test_author_across_multiple_repos():
    commits = {
        "repo-a": [_c("alice")],
        "repo-b": [_c("alice")],
    }
    summary = build_contributor_summary(commits)
    entry = summary.entries["alice"]
    assert entry.repo_count == 2
    assert "repo-a" in entry.repos
    assert "repo-b" in entry.repos


def test_top_contributor_is_most_commits():
    commits = {
        "repo-a": [_c("alice"), _c("alice"), _c("bob")],
    }
    summary = build_contributor_summary(commits)
    assert summary.top_contributor().author == "alice"


def test_sorted_entries_descending():
    commits = {
        "repo-a": [_c("bob"), _c("alice"), _c("alice"), _c("alice")],
    }
    summary = build_contributor_summary(commits)
    sorted_entries = summary.sorted_entries()
    assert sorted_entries[0].author == "alice"
    assert sorted_entries[1].author == "bob"


def test_format_contributor_summary_contains_author():
    commits = {"repo-a": [_c("alice")]}
    summary = build_contributor_summary(commits)
    output = format_contributor_summary(summary)
    assert "alice" in output
    assert "repo-a" in output


def test_format_contributor_summary_empty():
    summary = ContributorSummary()
    output = format_contributor_summary(summary)
    assert "No contributors" in output


def test_format_shows_total_contributors():
    commits = {"repo-a": [_c("alice"), _c("bob")]}
    summary = build_contributor_summary(commits)
    output = format_contributor_summary(summary)
    assert "Total contributors: 2" in output
