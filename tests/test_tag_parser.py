"""Tests for gitlog_digest.tag_parser."""

from datetime import datetime

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.tag_parser import (
    TaggedCommit,
    parse_commit,
    summarise_tags,
    KNOWN_TYPES,
)


def _commit(subject: str, sha: str = "abc1234") -> GitCommit:
    return GitCommit(
        sha=sha,
        author="Alice",
        date=datetime(2024, 3, 4, 10, 0, 0),
        subject=subject,
    )


def test_parse_feat_commit():
    tc = parse_commit(_commit("feat: add new parser"))
    assert tc.commit_type == "feat"
    assert tc.description == "add new parser"
    assert tc.scope is None
    assert tc.breaking is False


def test_parse_fix_with_scope():
    tc = parse_commit(_commit("fix(auth): handle null token"))
    assert tc.commit_type == "fix"
    assert tc.scope == "auth"
    assert tc.description == "handle null token"


def test_parse_breaking_change():
    tc = parse_commit(_commit("feat!: drop Python 3.8 support"))
    assert tc.breaking is True
    assert tc.commit_type == "feat"


def test_parse_breaking_with_scope():
    tc = parse_commit(_commit("refactor(core)!: rewrite internals"))
    assert tc.breaking is True
    assert tc.scope == "core"


def test_parse_non_conventional():
    tc = parse_commit(_commit("Updated README with examples"))
    assert tc.commit_type == "other"
    assert tc.description == "Updated README with examples"
    assert tc.scope is None
    assert tc.breaking is False


def test_type_label_known():
    tc = parse_commit(_commit("docs: fix typo"))
    assert tc.type_label == "Documentation"


def test_type_label_unknown():
    tc = parse_commit(_commit("wip: half done"))
    assert tc.type_label == "Other"


def test_summarise_tags_groups_by_type():
    commits = [
        _commit("feat: thing one", "aaa"),
        _commit("feat: thing two", "bbb"),
        _commit("fix: bug", "ccc"),
        _commit("random message", "ddd"),
    ]
    summary = summarise_tags(commits)
    assert len(summary.by_type["feat"]) == 2
    assert len(summary.by_type["fix"]) == 1
    assert len(summary.by_type["other"]) == 1
    assert summary.total == 4


def test_summarise_tags_breaking_changes():
    commits = [
        _commit("feat!: big change", "x1"),
        _commit("fix: small fix", "x2"),
        _commit("chore!: drop old api", "x3"),
    ]
    summary = summarise_tags(commits)
    assert len(summary.breaking_changes) == 2


def test_summarise_empty():
    summary = summarise_tags([])
    assert summary.total == 0
    assert summary.breaking_changes == []
