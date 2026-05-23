"""Tests for CommitImpactReport."""
from datetime import datetime

import pytest

from gitlog_digest.commit_impact import (
    CommitImpactReport,
    ImpactEntry,
    _impact_label,
    _impact_score,
)
from gitlog_digest.git_reader import GitCommit


def _c(sha: str, subject: str, author: str = "dev") -> GitCommit:
    return GitCommit(sha=sha, author=author, date=datetime(2024, 1, 15), subject=subject)


def test_score_zero_inputs():
    assert _impact_score(0, 0, 0) == 0.0


def test_score_files_weighted_double():
    assert _impact_score(3, 0, 0) == 6.0


def test_score_combined():
    assert _impact_score(2, 10, 5) == 19.0


def test_label_none():
    assert _impact_label(0) == "none"


def test_label_minor():
    assert _impact_label(5) == "minor"


def test_label_moderate():
    assert _impact_label(25) == "moderate"


def test_label_significant():
    assert _impact_label(100) == "significant"


def test_label_major():
    assert _impact_label(250) == "major"


def test_empty_report_total_zero():
    report = CommitImpactReport()
    assert report.total() == 0


def test_empty_report_average_is_zero():
    report = CommitImpactReport()
    assert report.average_score() == 0.0


def test_empty_report_peak_is_none():
    report = CommitImpactReport()
    assert report.peak() is None


def test_add_single_commit():
    report = CommitImpactReport()
    report.add_commit(_c("abc123", "feat: add thing"), files_changed=2, insertions=10, deletions=3)
    assert report.total() == 1


def test_single_commit_score_correct():
    report = CommitImpactReport()
    report.add_commit(_c("abc123", "feat: add thing"), files_changed=2, insertions=10, deletions=3)
    assert report.average_score() == pytest.approx(17.0)


def test_peak_returns_highest_score():
    report = CommitImpactReport()
    report.add_commit(_c("aaa", "small fix"), files_changed=1, insertions=1, deletions=0)
    report.add_commit(_c("bbb", "big refactor"), files_changed=10, insertions=100, deletions=80)
    peak = report.peak()
    assert peak is not None
    assert peak.sha == "bbb"


def test_top_returns_sorted_descending():
    report = CommitImpactReport()
    report.add_commit(_c("a", "minor"), files_changed=1, insertions=1, deletions=0)
    report.add_commit(_c("b", "large"), files_changed=5, insertions=50, deletions=30)
    report.add_commit(_c("c", "medium"), files_changed=3, insertions=20, deletions=5)
    top = report.top(2)
    assert len(top) == 2
    assert top[0].score >= top[1].score


def test_top_larger_than_entries_returns_all():
    report = CommitImpactReport()
    report.add_commit(_c("x", "one"), files_changed=1, insertions=1, deletions=0)
    assert len(report.top(10)) == 1


def test_by_label_counts():
    report = CommitImpactReport()
    report.add_commit(_c("a", "fix"), files_changed=0, insertions=0, deletions=0)
    report.add_commit(_c("b", "feat"), files_changed=1, insertions=3, deletions=0)
    labels = report.by_label()
    assert labels.get("none", 0) == 1
    assert labels.get("minor", 0) == 1


def test_impact_entry_str_contains_sha_and_label():
    entry = ImpactEntry(sha="deadbeef", author="alice", subject="chore: update", score=12.0, label="moderate")
    s = str(entry)
    assert "deadbee" in s
    assert "moderate" in s
