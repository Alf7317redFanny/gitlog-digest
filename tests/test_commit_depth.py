"""Tests for gitlog_digest.commit_depth."""
from __future__ import annotations

from datetime import datetime

import pytest

from gitlog_digest.commit_depth import (
    CommitDepthReport,
    _path_depth,
    build_depth_report,
    format_depth_report,
)
from gitlog_digest.git_reader import GitCommit


def _c(files: list[str]) -> GitCommit:
    return GitCommit(
        sha="abc1234",
        author="Dev",
        date=datetime(2024, 1, 15, 10, 0, 0),
        subject="chore: update files",
        changed_files=files,
        insertions=0,
        deletions=0,
    )


def test_path_depth_root_file():
    assert _path_depth("README.md") == 0


def test_path_depth_one_level():
    assert _path_depth("src/main.py") == 1


def test_path_depth_nested():
    assert _path_depth("a/b/c/file.py") == 3


def test_path_depth_trailing_slash_ignored():
    assert _path_depth("src/utils/helper.py") == 2


def test_empty_commits_returns_empty_report():
    report = build_depth_report([])
    assert report.total() == 0
    assert report.buckets() == []
    assert report.peak_depth() is None
    assert report.average_depth() is None


def test_single_commit_root_file():
    report = build_depth_report([_c(["README.md"])])
    assert report.total() == 1
    assert len(report.buckets()) == 1
    assert report.buckets()[0].depth == 0
    assert report.buckets()[0].count == 1


def test_multiple_files_different_depths():
    report = build_depth_report([_c(["README.md", "src/main.py", "src/utils/helper.py"])])
    assert report.total() == 3
    depths = {b.depth: b.count for b in report.buckets()}
    assert depths[0] == 1
    assert depths[1] == 1
    assert depths[2] == 1


def test_peak_depth_returns_most_common():
    report = build_depth_report([
        _c(["src/a.py", "src/b.py", "src/c.py", "README.md"])
    ])
    assert report.peak_depth() == 1


def test_average_depth_computed_correctly():
    report = build_depth_report([_c(["README.md", "src/main.py"])])
    # depths: 0 + 1 = 1, count = 2, avg = 0.5
    assert report.average_depth() == pytest.approx(0.5)


def test_buckets_sorted_by_depth():
    report = build_depth_report([_c(["a/b/c/d.py", "a/b.py", "z.py"])])
    depths = [b.depth for b in report.buckets()]
    assert depths == sorted(depths)


def test_merge_combines_counts():
    r1 = build_depth_report([_c(["src/a.py"])])
    r2 = build_depth_report([_c(["src/b.py", "README.md"])])
    merged = r1.merge(r2)
    assert merged.total() == 3
    depths = {b.depth: b.count for b in merged.buckets()}
    assert depths[1] == 2
    assert depths[0] == 1


def test_merge_with_empty_report():
    r1 = build_depth_report([_c(["src/a.py"])])
    r2 = CommitDepthReport()
    merged = r1.merge(r2)
    assert merged.total() == r1.total()


def test_format_depth_report_contains_title():
    report = build_depth_report([_c(["src/main.py"])])
    text = format_depth_report(report, title="Depth Report")
    assert "Depth Report" in text


def test_format_depth_report_empty_shows_no_data():
    report = CommitDepthReport()
    text = format_depth_report(report)
    assert "no data" in text


def test_format_depth_report_shows_avg():
    report = build_depth_report([_c(["README.md", "src/main.py"])])
    text = format_depth_report(report)
    assert "avg depth" in text
