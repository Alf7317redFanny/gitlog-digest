"""Tests for CommitHotspotReport."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from gitlog_digest.commit_hotspot import (
    CommitHotspotReport,
    HotspotEntry,
    build_hotspot_report,
    format_hotspot_report,
)
from gitlog_digest.git_reader import GitCommit


def _c(files: list[str], msg: str = "chore: update") -> GitCommit:
    return GitCommit(
        sha="abc1234",
        short_sha="abc1234"[:7],
        subject=msg,
        author="Dev",
        date=datetime(2024, 3, 4, tzinfo=timezone.utc),
        files_changed=files,
        insertions=0,
        deletions=0,
        branch="main",
    )


def test_empty_commits_returns_empty_report():
    report = build_hotspot_report([])
    assert report.total_files() == 0
    assert report.top() == []
    assert report.peak() is None


def test_single_commit_single_file():
    report = build_hotspot_report([_c(["src/app.py"])])
    assert report.total_files() == 1
    assert report.peak().path == "src/app.py"
    assert report.peak().count == 1


def test_multiple_commits_same_file_increments_count():
    commits = [_c(["src/app.py"]), _c(["src/app.py"]), _c(["src/app.py"])]
    report = build_hotspot_report(commits)
    assert report.peak().count == 3


def test_multiple_files_sorted_by_frequency():
    commits = [
        _c(["a.py", "b.py"]),
        _c(["a.py"]),
        _c(["b.py", "c.py"]),
        _c(["b.py"]),
    ]
    report = build_hotspot_report(commits)
    top = report.top(3)
    assert top[0].path == "b.py"
    assert top[0].count == 3
    assert top[1].path == "a.py"
    assert top[1].count == 2


def test_top_n_limits_results():
    commits = [_c([f"file{i}.py"]) for i in range(20)]
    report = build_hotspot_report(commits)
    assert len(report.top(5)) == 5


def test_len_returns_total_files():
    commits = [_c(["x.py", "y.py"]), _c(["z.py"])]
    report = build_hotspot_report(commits)
    assert len(report) == 3


def test_format_hotspot_report_contains_filename():
    report = build_hotspot_report([_c(["README.md"])])
    text = format_hotspot_report(report)
    assert "README.md" in text


def test_format_hotspot_report_empty():
    report = build_hotspot_report([])
    text = format_hotspot_report(report)
    assert "none" in text.lower()


def test_hotspot_entry_str():
    entry = HotspotEntry(path="src/main.py", count=7)
    assert "src/main.py" in str(entry)
    assert "7" in str(entry)
