"""Tests for gitlog_digest.commit_label."""
from __future__ import annotations

import pytest
from datetime import datetime
from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_label import (
    _detect_label,
    build_label_report,
    format_label_report,
    CommitLabelReport,
)


def _c(subject: str, author: str = "Alice") -> GitCommit:
    return GitCommit(
        sha="abc1234",
        author=author,
        date=datetime(2024, 6, 3, 10, 0, 0),
        subject=subject,
        files_changed=[],
        insertions=0,
        deletions=0,
    )


def test_detect_label_feat():
    assert _detect_label("feat: add login page") == "Feature"


def test_detect_label_fix_with_scope():
    assert _detect_label("fix(auth): correct token expiry") == "Bug Fix"


def test_detect_label_docs():
    assert _detect_label("docs: update README") == "Documentation"


def test_detect_label_unknown_returns_other():
    assert _detect_label("initial commit") == "Other"


def test_detect_label_case_insensitive():
    assert _detect_label("FEAT: new dashboard") == "Feature"


def test_detect_label_chore():
    assert _detect_label("chore: bump dependencies") == "Chore"


def test_detect_label_revert():
    assert _detect_label("revert: undo last change") == "Revert"


def test_empty_commits_returns_empty_report():
    report = build_label_report([])
    assert report.total() == 0
    assert report.labels() == []


def test_single_commit_classified_correctly():
    report = build_label_report([_c("feat: add search")])
    assert report.total() == 1
    assert "Feature" in report.labels()
    entry = report.entry_for("Feature")
    assert entry is not None
    assert entry.count == 1


def test_multiple_commits_same_label():
    commits = [_c("fix: null check"), _c("fix(ui): button color")]
    report = build_label_report(commits)
    assert report.entry_for("Bug Fix").count == 2


def test_multiple_labels_tracked_independently():
    commits = [
        _c("feat: new endpoint"),
        _c("fix: crash on startup"),
        _c("docs: add examples"),
    ]
    report = build_label_report(commits)
    assert report.total() == 3
    assert report.entry_for("Feature").count == 1
    assert report.entry_for("Bug Fix").count == 1
    assert report.entry_for("Documentation").count == 1


def test_top_returns_sorted_by_count():
    commits = [
        _c("feat: a"), _c("feat: b"), _c("feat: c"),
        _c("fix: x"), _c("fix: y"),
        _c("docs: z"),
    ]
    report = build_label_report(commits)
    top = report.top(2)
    assert top[0].label == "Feature"
    assert top[0].count == 3
    assert top[1].label == "Bug Fix"
    assert top[1].count == 2


def test_as_dict_returns_correct_mapping():
    commits = [_c("chore: lint"), _c("chore: format"), _c("test: add unit tests")]
    report = build_label_report(commits)
    d = report.as_dict()
    assert d["Chore"] == 2
    assert d["Test"] == 1


def test_format_label_report_contains_label_name():
    commits = [_c("perf: optimise query")]
    report = build_label_report(commits)
    text = format_label_report(report)
    assert "Performance" in text


def test_format_label_report_empty():
    report = CommitLabelReport()
    text = format_label_report(report)
    assert "No commits" in text
