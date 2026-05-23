"""Integration tests for commit impact across multiple repos."""
from datetime import datetime

from gitlog_digest.commit_impact import CommitImpactReport
from gitlog_digest.git_reader import GitCommit
from gitlog_digest.impact_integration import (
    combined_impact,
    format_all_impact_reports,
    impact_per_repo,
    impact_report_dict,
)


def _c(sha: str, subject: str, author: str = "dev") -> GitCommit:
    return GitCommit(sha=sha, author=author, date=datetime(2024, 1, 15), subject=subject)


_COMMITS = {
    "repo-a": [_c("aaa", "feat: alpha"), _c("bbb", "fix: beta")],
    "repo-b": [_c("ccc", "chore: gamma")],
}

_DIFFS = {
    "repo-a": [(2, 10, 5), (1, 2, 1)],
    "repo-b": [(8, 80, 40)],
}


def test_impact_per_repo_keys_match_input():
    reports = impact_per_repo(_COMMITS, _DIFFS)
    assert set(reports.keys()) == {"repo-a", "repo-b"}


def test_impact_per_repo_totals():
    reports = impact_per_repo(_COMMITS, _DIFFS)
    assert reports["repo-a"].total() == 2
    assert reports["repo-b"].total() == 1


def test_impact_per_repo_uses_diff_data():
    reports = impact_per_repo(_COMMITS, _DIFFS)
    peak_a = reports["repo-a"].peak()
    assert peak_a is not None
    assert peak_a.sha == "aaa"


def test_combined_impact_total():
    report = combined_impact(_COMMITS, _DIFFS)
    assert report.total() == 3


def test_combined_impact_peak_is_repo_b():
    report = combined_impact(_COMMITS, _DIFFS)
    peak = report.peak()
    assert peak is not None
    assert peak.sha == "ccc"


def test_impact_report_dict_structure():
    report = combined_impact(_COMMITS, _DIFFS)
    d = impact_report_dict(report)
    assert "total" in d
    assert "average_score" in d
    assert "by_label" in d
    assert "peak" in d
    assert "top" in d


def test_impact_report_dict_peak_not_none():
    report = combined_impact(_COMMITS, _DIFFS)
    d = impact_report_dict(report)
    assert d["peak"] is not None
    assert "sha" in d["peak"]


def test_impact_report_dict_empty_report():
    report = CommitImpactReport()
    d = impact_report_dict(report)
    assert d["total"] == 0
    assert d["peak"] is None
    assert d["top"] == []


def test_format_all_impact_reports_contains_repo_names():
    reports = impact_per_repo(_COMMITS, _DIFFS)
    text = format_all_impact_reports(reports)
    assert "repo-a" in text
    assert "repo-b" in text


def test_format_all_impact_reports_empty_repo():
    reports = {"empty-repo": CommitImpactReport()}
    text = format_all_impact_reports(reports)
    assert "no commits" in text


def test_missing_diff_data_defaults_to_zero():
    reports = impact_per_repo({"repo-a": [_c("zzz", "fix: thing")]}, {})
    assert reports["repo-a"].total() == 1
    assert reports["repo-a"].average_score() == 0.0
