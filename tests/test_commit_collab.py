"""Tests for commit_collab and collab_integration."""
from __future__ import annotations

from datetime import datetime
from typing import List

import pytest

from gitlog_digest.commit_collab import (
    build_collab_report,
    format_collab_report,
    CommitCollabReport,
)
from gitlog_digest.collab_integration import (
    collab_per_repo,
    combined_collab,
    collab_report_dict,
)
from gitlog_digest.git_reader import GitCommit

_TS = datetime(2024, 3, 11, 10, 0, 0)


def _c(author: str, files: List[str]) -> GitCommit:
    return GitCommit(
        sha="abc1234",
        author=author,
        date=_TS,
        subject="chore: update",
        files=files,
    )


def test_empty_commits_returns_empty_report():
    report = build_collab_report([])
    assert report.total_pairs() == 0
    assert report.top() == []


def test_single_author_no_pair():
    commits = [_c("Alice", ["src/a.py", "src/b.py"])]
    report = build_collab_report(commits)
    assert report.total_pairs() == 0


def test_two_authors_same_file_creates_pair():
    commits = [
        _c("Alice", ["src/a.py"]),
        _c("Bob", ["src/a.py"]),
    ]
    report = build_collab_report(commits)
    assert report.total_pairs() == 1
    top = report.top()
    assert top[0].author_a == "Alice"
    assert top[0].author_b == "Bob"
    assert top[0].shared_files == 1


def test_pair_count_increases_with_more_shared_files():
    commits = [
        _c("Alice", ["src/a.py", "src/b.py"]),
        _c("Bob", ["src/a.py", "src/b.py"]),
    ]
    report = build_collab_report(commits)
    top = report.top()
    assert top[0].shared_files == 2


def test_top_n_limits_results():
    files = [f"file{i}.py" for i in range(10)]
    commits = [_c("Alice", files), _c("Bob", files[:5]), _c("Carol", files[:3])]
    report = build_collab_report(commits)
    assert len(report.top(2)) == 2


def test_format_report_no_pairs():
    report = build_collab_report([])
    text = format_collab_report(report)
    assert "no shared" in text.lower()


def test_format_report_contains_authors():
    commits = [_c("Alice", ["x.py"]), _c("Bob", ["x.py"])]
    report = build_collab_report(commits)
    text = format_collab_report(report)
    assert "Alice" in text
    assert "Bob" in text


def test_collab_per_repo_keys_match_input():
    data = {
        "repo-a": [_c("Alice", ["a.py"]), _c("Bob", ["a.py"])],
        "repo-b": [_c("Carol", ["b.py"])],
    }
    result = collab_per_repo(data)
    assert set(result.keys()) == {"repo-a", "repo-b"}


def test_combined_collab_merges_all_commits():
    data = {
        "repo-a": [_c("Alice", ["shared.py"])],
        "repo-b": [_c("Bob", ["shared.py"])],
    }
    report = combined_collab(data)
    assert report.total_pairs() == 1


def test_collab_report_dict_structure():
    data = {
        "repo-x": [_c("Alice", ["f.py"]), _c("Bob", ["f.py"])],
    }
    d = collab_report_dict(data)
    assert "repos" in d
    assert "combined" in d
    assert "repo-x" in d["repos"]
