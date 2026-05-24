"""Tests for momentum_integration.py"""
import pytest
from datetime import datetime
from typing import List

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.momentum_integration import (
    momentum_per_repo,
    combined_momentum,
    momentum_report_dict,
    format_all_momentum_reports,
)


def _c(author: str) -> GitCommit:
    return GitCommit(
        sha="deadbeef",
        short_sha="deadbee",
        author=author,
        date=datetime(2024, 3, 4, 9, 0),
        subject="fix: something",
        files_changed=["src/main.py"],
        insertions=3,
        deletions=1,
        branch="main",
    )


def test_momentum_per_repo_keys_match_input():
    current = {"repo-a": [_c("alice")], "repo-b": [_c("bob")]}
    previous = {"repo-a": [_c("alice"), _c("alice")]}
    result = momentum_per_repo(current, previous)
    assert set(result.keys()) == {"repo-a", "repo-b"}


def test_momentum_per_repo_missing_previous_defaults_to_empty():
    current = {"repo-x": [_c("carol"), _c("carol"), _c("carol")]}
    previous = {}
    result = momentum_per_repo(current, previous)
    entry = result["repo-x"].entries()[0]
    assert entry.previous_count == 0
    assert entry.current_count == 3


def test_combined_momentum_merges_all():
    current = [_c("alice"), _c("alice"), _c("bob")]
    previous = [_c("alice"), _c("bob"), _c("bob")]
    report = combined_momentum(current, previous)
    authors = {e.author for e in report.entries()}
    assert "alice" in authors
    assert "bob" in authors


def test_combined_momentum_empty_input():
    report = combined_momentum([], [])
    assert len(report) == 0


def test_momentum_report_dict_structure():
    current = [_c("dave"), _c("dave")]
    previous = [_c("dave")]
    report = combined_momentum(current, previous)
    d = momentum_report_dict(report)
    assert "overall_trend" in d
    assert "total_delta" in d
    assert "authors" in d
    assert d["authors"][0]["author"] == "dave"


def test_momentum_report_dict_delta_values():
    current = [_c("eve")]
    previous = [_c("eve"), _c("eve"), _c("eve")]
    report = combined_momentum(current, previous)
    d = momentum_report_dict(report)
    assert d["total_delta"] == -2
    assert d["overall_trend"] == "down"


def test_format_all_momentum_reports_contains_repo_names():
    current = {"alpha": [_c("alice")], "beta": [_c("bob"), _c("bob")]}
    previous = {"alpha": [_c("alice"), _c("alice")], "beta": [_c("bob")]}
    reports = momentum_per_repo(current, previous)
    text = format_all_momentum_reports(reports)
    assert "alpha" in text
    assert "beta" in text


def test_format_all_momentum_reports_empty_input():
    text = format_all_momentum_reports({})
    assert text == ""
