"""Tests for gitlog_digest.commit_complexity."""
import pytest
from datetime import datetime

from gitlog_digest.commit_complexity import (
    CommitComplexityReport,
    ComplexityEntry,
    _label,
    _score,
)
from gitlog_digest.git_reader import GitCommit


def _c(sha="abc1234", author="Alice", subject="fix: something") -> GitCommit:
    return GitCommit(sha=sha, author=author, date=datetime(2024, 3, 1), subject=subject)


def test_score_zero_inputs():
    assert _score(0, 0, 0) == 0


def test_score_files_weighted_double():
    assert _score(0, 0, 3) == 6


def test_score_combined():
    assert _score(5, 3, 2) == 12


def test_label_trivial():
    assert _label(0) == "trivial"
    assert _label(9) == "trivial"


def test_label_moderate():
    assert _label(10) == "moderate"
    assert _label(49) == "moderate"


def test_label_complex():
    assert _label(50) == "complex"
    assert _label(200) == "complex"


def test_empty_report_total_is_zero():
    r = CommitComplexityReport()
    assert r.total() == 0


def test_empty_report_average_is_zero():
    r = CommitComplexityReport()
    assert r.average_score() == 0.0


def test_add_single_commit_trivial():
    r = CommitComplexityReport()
    r.add_commit(_c(), insertions=1, deletions=1, files_changed=1)
    assert r.total() == 1
    assert r.by_label("trivial") != []


def test_add_complex_commit():
    r = CommitComplexityReport()
    r.add_commit(_c(), insertions=30, deletions=20, files_changed=5)
    assert r.by_label("complex")[0].score == 60


def test_average_score_multiple():
    r = CommitComplexityReport()
    r.add_commit(_c(sha="a"), insertions=0, deletions=0, files_changed=0)
    r.add_commit(_c(sha="b"), insertions=10, deletions=10, files_changed=5)
    # scores: 0, 30 -> avg 15
    assert r.average_score() == 15.0


def test_top_returns_sorted_descending():
    r = CommitComplexityReport()
    r.add_commit(_c(sha="a"), insertions=5, deletions=0, files_changed=0)
    r.add_commit(_c(sha="b"), insertions=100, deletions=0, files_changed=0)
    r.add_commit(_c(sha="c"), insertions=20, deletions=0, files_changed=0)
    top = r.top(2)
    assert top[0].score > top[1].score


def test_by_label_filters_correctly():
    r = CommitComplexityReport()
    r.add_commit(_c(sha="a"), insertions=0, deletions=0, files_changed=0)
    r.add_commit(_c(sha="b"), insertions=100, deletions=50, files_changed=10)
    assert len(r.by_label("trivial")) == 1
    assert len(r.by_label("complex")) == 1


def test_entry_str_contains_sha_and_label():
    e = ComplexityEntry(sha="abc1234xyz", author="Bob", subject="feat: x", score=60, label="complex")
    s = str(e)
    assert "abc1234" in s
    assert "complex" in s
