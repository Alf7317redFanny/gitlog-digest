"""Tests for commit_coupling and coupling_integration."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from gitlog_digest.commit_coupling import (
    CommitCouplingReport,
    build_coupling_report,
    format_coupling_report,
)
from gitlog_digest.coupling_integration import (
    combined_coupling,
    coupling_per_repo,
    coupling_report_dict,
)
from gitlog_digest.git_reader import GitCommit

_TS = datetime(2024, 3, 1, 10, 0, tzinfo=timezone.utc)


def _c(sha: str, files: list[str]) -> GitCommit:
    return GitCommit(sha=sha, author="dev", timestamp=_TS, subject="msg", files_changed=files)


def test_empty_commits_returns_empty_report():
    report = build_coupling_report([])
    assert len(report) == 0
    assert report.top() == []


def test_single_file_commit_not_counted():
    report = build_coupling_report([_c("a", ["foo.py"])])
    assert len(report) == 0


def test_two_files_creates_one_pair():
    report = build_coupling_report([_c("a", ["foo.py", "bar.py"])])
    assert len(report) == 1
    top = report.top()
    assert top[0].file_a == "bar.py"
    assert top[0].file_b == "foo.py"
    assert top[0].count == 1


def test_repeated_pair_increments_count():
    commits = [
        _c("a", ["x.py", "y.py"]),
        _c("b", ["x.py", "y.py"]),
        _c("c", ["x.py", "y.py"]),
    ]
    report = build_coupling_report(commits)
    assert report.top(1)[0].count == 3


def test_three_files_creates_three_pairs():
    report = build_coupling_report([_c("a", ["a.py", "b.py", "c.py"])])
    assert len(report) == 3


def test_top_n_limits_results():
    commits = [
        _c("a", ["a.py", "b.py"]),
        _c("b", ["a.py", "b.py"]),
        _c("c", ["c.py", "d.py"]),
    ]
    report = build_coupling_report(commits)
    assert len(report.top(1)) == 1
    assert report.top(1)[0].count == 2


def test_duplicate_files_in_commit_deduplicated():
    report = build_coupling_report([_c("a", ["x.py", "x.py", "y.py"])])
    assert len(report) == 1


def test_format_coupling_report_empty():
    report = CommitCouplingReport()
    text = format_coupling_report(report)
    assert "No file coupling" in text


def test_format_coupling_report_contains_files():
    report = build_coupling_report([_c("a", ["alpha.py", "beta.py"])])
    text = format_coupling_report(report)
    assert "alpha.py" in text
    assert "beta.py" in text


def test_coupling_per_repo_keys_match_input():
    data = {
        "repo-a": [_c("1", ["f.py", "g.py"])],
        "repo-b": [_c("2", ["h.py", "i.py"])],
    }
    result = coupling_per_repo(data)
    assert set(result.keys()) == {"repo-a", "repo-b"}


def test_combined_coupling_merges_repos():
    data = {
        "repo-a": [_c("1", ["x.py", "y.py"])],
        "repo-b": [_c("2", ["x.py", "y.py"])],
    }
    combined = combined_coupling(data)
    assert combined.top(1)[0].count == 2


def test_coupling_report_dict_structure():
    data = {"repo": [_c("1", ["a.py", "b.py"])]}
    d = coupling_report_dict(data)
    assert "per_repo" in d
    assert "combined" in d
    assert "total_unique_pairs" in d
    assert d["total_unique_pairs"] == 1
