"""Unit tests for gitlog_digest.word_cloud."""

import pytest
from datetime import datetime

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.word_cloud import (
    WordCloudReport,
    _tokenise,
    build_word_cloud,
    format_word_cloud_text,
    word_cloud_dict,
)


def _c(subject: str) -> GitCommit:
    return GitCommit(
        sha="abc1234",
        subject=subject,
        author="dev",
        date=datetime(2024, 1, 15, 10, 0),
    )


# --- tokeniser ---

def test_tokenise_lowercases():
    assert "fix" in _tokenise("Fix the bug")


def test_tokenise_removes_stop_words():
    tokens = _tokenise("fix the bug in the module")
    assert "the" not in tokens
    assert "in" not in tokens


def test_tokenise_skips_short_words():
    tokens = _tokenise("do it now")
    assert "it" not in tokens


def test_tokenise_returns_empty_for_blank():
    assert _tokenise("") == []


# --- build_word_cloud ---

def test_empty_commits_returns_empty_report():
    report = build_word_cloud([])
    assert len(report) == 0
    assert report.total_words == 0


def test_single_commit_counted():
    report = build_word_cloud([_c("refactor authentication module")])
    assert report.counts["refactor"] == 1
    assert report.counts["authentication"] == 1
    assert report.counts["module"] == 1


def test_repeated_word_accumulates():
    commits = [_c("fix login bug"), _c("fix signup bug"), _c("fix reset bug")]
    report = build_word_cloud(commits)
    assert report.counts["fix"] == 3
    assert report.counts["bug"] == 3


def test_top_returns_most_common():
    commits = [_c("add feature"), _c("add test"), _c("fix bug")]
    report = build_word_cloud(commits)
    top = report.top(1)
    assert top[0][0] == "add"
    assert top[0][1] == 2


def test_top_n_limits_results():
    commits = [_c(f"word{i} commit message") for i in range(20)]
    report = build_word_cloud(commits)
    assert len(report.top(5)) <= 5


# --- word_cloud_dict ---

def test_word_cloud_dict_structure():
    report = build_word_cloud([_c("add feature flag")])
    d = word_cloud_dict(report)
    assert "total_unique_words" in d
    assert "total_word_occurrences" in d
    assert "top_words" in d
    assert isinstance(d["top_words"], list)


# --- format_word_cloud_text ---

def test_format_contains_header():
    report = build_word_cloud([_c("add feature")])
    text = format_word_cloud_text(report)
    assert "Keywords" in text


def test_format_empty_shows_no_data():
    report = WordCloudReport()
    text = format_word_cloud_text(report)
    assert "no data" in text
