"""Tests for timezone_integration module."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from gitlog_digest.timezone_integration import (
    reports_per_repo,
    combined_report,
    timezone_report_dict,
    format_all_timezone_reports,
)
from gitlog_digest.git_reader import GitCommit


def _c(offset_hours: float = 0) -> GitCommit:
    tz = timezone(timedelta(hours=offset_hours))
    return GitCommit(
        sha="def5678",
        author="Dev",
        author_date=datetime(2024, 6, 3, 12, 0, 0, tzinfo=tz),
        subject="feat: something",
        files_changed=[],
        insertions=5,
        deletions=2,
        branch="main",
    )


def test_reports_per_repo_keys_match_input():
    data = {"repo-a": [_c(0)], "repo-b": [_c(1)]}
    result = reports_per_repo(data)
    assert set(result.keys()) == {"repo-a", "repo-b"}


def test_reports_per_repo_totals():
    data = {"repo-a": [_c(0), _c(0)], "repo-b": [_c(2)]}
    result = reports_per_repo(data)
    assert result["repo-a"].total == 2
    assert result["repo-b"].total == 1


def test_combined_report_total():
    data = {"repo-a": [_c(0), _c(1)], "repo-b": [_c(2)]}
    report = combined_report(data)
    assert report.total == 3


def test_combined_report_merges_offsets():
    data = {"repo-a": [_c(1)], "repo-b": [_c(1), _c(2)]}
    report = combined_report(data)
    assert report.entry_for(60).count == 2
    assert report.entry_for(120).count == 1


def test_combined_report_empty_input():
    report = combined_report({})
    assert report.total == 0


def test_timezone_report_dict_keys():
    data = {"repo": [_c(0), _c(1)]}
    d = timezone_report_dict(combined_report(data))
    assert "total_commits" in d
    assert "unique_offsets" in d
    assert "top_offsets" in d


def test_timezone_report_dict_values():
    data = {"repo": [_c(0), _c(0), _c(1)]}
    d = timezone_report_dict(combined_report(data))
    assert d["total_commits"] == 3
    assert d["unique_offsets"] == 2


def test_format_all_timezone_reports_contains_repo_name():
    data = {"my-repo": [_c(0)]}
    text = format_all_timezone_reports(data)
    assert "my-repo" in text


def test_format_all_timezone_reports_contains_combined():
    data = {"repo-x": [_c(0)]}
    text = format_all_timezone_reports(data)
    assert "Combined" in text


def test_format_all_timezone_reports_empty_repo():
    data = {"empty": []}
    text = format_all_timezone_reports(data)
    assert "no commits" in text
