"""Tests for gitlog_digest.pattern_integration."""
from __future__ import annotations

from datetime import datetime

import pytest

from gitlog_digest.commit_pattern import build_pattern_report
from gitlog_digest.pattern_integration import (
    combined_pattern,
    format_all_pattern_reports,
    pattern_report_dict,
    patterns_per_repo,
)
from gitlog_digest.git_reader import GitCommit


def _c(subject: str, author: str = "Alice") -> GitCommit:
    return GitCommit(
        sha="deadbeef",
        subject=subject,
        author=author,
        date=datetime.fromisoformat("2024-03-06T12:00:00+00:00"),
    )


_REPO_COMMITS = {
    "alpha": [_c("feat: init"), _c("fix: crash"), _c("fix: edge case")],
    "beta": [_c("chore: deps"), _c("feat: widget")],
}


def test_patterns_per_repo_keys_match_input():
    result = patterns_per_repo(_REPO_COMMITS)
    assert set(result.keys()) == {"alpha", "beta"}


def test_patterns_per_repo_totals():
    result = patterns_per_repo(_REPO_COMMITS)
    assert result["alpha"].total == 3
    assert result["beta"].total == 2


def test_combined_pattern_total():
    per_repo = patterns_per_repo(_REPO_COMMITS)
    merged = combined_pattern(per_repo)
    assert merged.total == 5


def test_combined_pattern_top_type():
    per_repo = patterns_per_repo(_REPO_COMMITS)
    merged = combined_pattern(per_repo)
    # fix: 2, feat: 2, chore: 1 — fix and feat tied; max picks deterministically
    assert merged.top_type in {"fix", "feat"}


def test_pattern_report_dict_structure():
    report = build_pattern_report([_c("feat: x"), _c("fix: y")])
    d = pattern_report_dict(report)
    assert "total_typed_commits" in d
    assert "top_type" in d
    assert isinstance(d["types"], list)
    assert d["total_typed_commits"] == 2


def test_pattern_report_dict_peak_day_is_iso_string():
    report = build_pattern_report([_c("feat: x")])
    d = pattern_report_dict(report)
    entry = next(e for e in d["types"] if e["type"] == "feat")
    assert entry["peak_day"] == "2024-03-06"


def test_format_all_pattern_reports_contains_repo_names():
    per_repo = patterns_per_repo(_REPO_COMMITS)
    text = format_all_pattern_reports(per_repo)
    assert "alpha" in text
    assert "beta" in text


def test_format_all_pattern_reports_with_merged():
    per_repo = patterns_per_repo(_REPO_COMMITS)
    merged = combined_pattern(per_repo)
    text = format_all_pattern_reports(per_repo, merged)
    assert "combined" in text


def test_format_empty_repo_shows_no_conventional_commits():
    per_repo = {"empty-repo": build_pattern_report([_c("wip stuff")])}
    text = format_all_pattern_reports(per_repo)
    assert "no conventional commits" in text
