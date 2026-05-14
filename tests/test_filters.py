"""Tests for gitlog_digest.filters."""

import pytest
from gitlog_digest.git_reader import GitCommit
from gitlog_digest.filters import (
    CommitFilter,
    apply_filter,
    filter_by_author,
    exclude_merge_commits,
)


def make_commit(sha="abc1234", author="Alice", subject="fix: something"):
    return GitCommit(sha=sha, author=author, date="2024-01-15", subject=subject)


ALICE = make_commit(sha="aaa0001", author="Alice", subject="feat: add widget")
BOB = make_commit(sha="bbb0002", author="Bob", subject="fix: typo")
MERGE = make_commit(sha="ccc0003", author="Alice", subject="Merge branch 'main'")
CHORE = make_commit(sha="ddd0004", author="Carol", subject="chore: update deps")

ALL_COMMITS = [ALICE, BOB, MERGE, CHORE]


def test_no_filter_returns_all():
    result = apply_filter(ALL_COMMITS, CommitFilter())
    assert result == ALL_COMMITS


def test_filter_by_single_author():
    result = filter_by_author(ALL_COMMITS, "Alice")
    assert result == [ALICE, MERGE]


def test_filter_by_author_case_insensitive():
    result = filter_by_author(ALL_COMMITS, "alice")
    assert result == [ALICE, MERGE]


def test_filter_multiple_authors():
    result = apply_filter(ALL_COMMITS, CommitFilter(authors=["Alice", "Bob"]))
    assert result == [ALICE, BOB, MERGE]


def test_exclude_authors():
    result = apply_filter(ALL_COMMITS, CommitFilter(exclude_authors=["Bob", "Carol"]))
    assert result == [ALICE, MERGE]


def test_exclude_merges():
    result = exclude_merge_commits(ALL_COMMITS)
    assert MERGE not in result
    assert len(result) == 3


def test_message_contains():
    result = apply_filter(ALL_COMMITS, CommitFilter(message_contains="typo"))
    assert result == [BOB]


def test_message_contains_case_insensitive():
    result = apply_filter(ALL_COMMITS, CommitFilter(message_contains="TYPO"))
    assert result == [BOB]


def test_combined_filter_author_and_no_merges():
    result = apply_filter(
        ALL_COMMITS, CommitFilter(authors=["Alice"], exclude_merges=True)
    )
    assert result == [ALICE]


def test_empty_commit_list():
    result = apply_filter([], CommitFilter(authors=["Alice"], exclude_merges=True))
    assert result == []
