"""Tests for gitlog_digest.complexity_integration."""
from datetime import datetime
from typing import List

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.complexity_integration import (
    complexity_per_repo,
    combined_complexity,
    complexity_report_dict,
    format_all_complexity_reports,
)


def _c(sha="abc1234", author="Alice", subject="fix: something") -> GitCommit:
    return GitCommit(sha=sha, author=author, date=datetime(2024, 3, 1), subject=subject)


def test_complexity_per_repo_keys_match_input():
    data = {"repo-a": [_c(sha="a")], "repo-b": [_c(sha="b")]}
    reports = complexity_per_repo(data)
    assert set(reports.keys()) == {"repo-a", "repo-b"}


def test_complexity_per_repo_totals():
    data = {"repo-a": [_c(sha="a"), _c(sha="b")]}
    reports = complexity_per_repo(data)
    assert reports["repo-a"].total() == 2


def test_complexity_per_repo_uses_diff_data():
    data = {"repo-a": [_c(sha="abc")]}
    diff = {"repo-a": [{"sha": "abc", "insertions": 100, "deletions": 50, "files_changed": 10}]}
    reports = complexity_per_repo(data, diff_data=diff)
    entry = reports["repo-a"].entries()[0]
    assert entry.score == 170  # 100+50+10*2
    assert entry.label == "complex"


def test_combined_complexity_total():
    data = {"repo-a": [_c(sha="a"), _c(sha="b")], "repo-b": [_c(sha="c")]}
    reports = complexity_per_repo(data)
    combined = combined_complexity(reports)
    assert combined.total() == 3


def test_combined_complexity_empty_input():
    combined = combined_complexity({})
    assert combined.total() == 0
    assert combined.average_score() == 0.0


def test_report_dict_keys():
    data = {"repo-a": [_c()]}
    reports = complexity_per_repo(data)
    d = complexity_report_dict(reports["repo-a"])
    assert "total" in d
    assert "average_score" in d
    assert "trivial" in d
    assert "moderate" in d
    assert "complex" in d
    assert "top_complex" in d


def test_report_dict_counts_sum_to_total():
    data = {"repo-a": [_c(sha="a"), _c(sha="b"), _c(sha="c")]}
    diff = {
        "repo-a": [
            {"sha": "a", "insertions": 0, "deletions": 0, "files_changed": 0},
            {"sha": "b", "insertions": 20, "deletions": 5, "files_changed": 2},
            {"sha": "c", "insertions": 80, "deletions": 40, "files_changed": 10},
        ]
    }
    reports = complexity_per_repo(data, diff_data=diff)
    d = complexity_report_dict(reports["repo-a"])
    assert d["trivial"] + d["moderate"] + d["complex"] == d["total"]


def test_format_all_contains_repo_name():
    data = {"my-repo": [_c()]}
    reports = complexity_per_repo(data)
    text = format_all_complexity_reports(reports)
    assert "my-repo" in text


def test_format_all_contains_complexity_header():
    data = {"my-repo": [_c()]}
    reports = complexity_per_repo(data)
    text = format_all_complexity_reports(reports)
    assert "Complexity" in text
