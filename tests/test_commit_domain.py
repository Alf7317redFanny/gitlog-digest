"""Tests for commit_domain.py"""
import pytest
from datetime import datetime
from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_domain import (
    _detect_domain,
    build_domain_report,
    domain_report_dict,
    CommitDomainReport,
)


def _c(files: list[str]) -> GitCommit:
    return GitCommit(
        sha="abc1234",
        author="Dev",
        date=datetime(2024, 6, 10, 12, 0, 0),
        subject="chore: update stuff",
        files_changed=files,
        insertions=1,
        deletions=0,
    )


def test_detect_domain_test_files():
    assert _detect_domain(["tests/test_foo.py", "tests/test_bar.py"]) == "test"


def test_detect_domain_docs_files():
    assert _detect_domain(["docs/guide.md", "docs/api.md"]) == "docs"


def test_detect_domain_ci_files():
    assert _detect_domain([".github/workflows/ci.yml"]) == "ci"


def test_detect_domain_frontend_files():
    assert _detect_domain(["src/components/Button.tsx", "src/pages/Home.tsx"]) == "frontend"


def test_detect_domain_unknown_returns_none():
    assert _detect_domain(["some/random/path/file.txt"]) is None


def test_detect_domain_empty_returns_none():
    assert _detect_domain([]) is None


def test_detect_domain_majority_wins():
    files = ["tests/a.py", "tests/b.py", "docs/readme.md"]
    assert _detect_domain(files) == "test"


def test_empty_commits_returns_empty_report():
    report = build_domain_report([])
    assert report.total() == 0
    assert report.unclassified == 0
    assert report.top() == []


def test_single_commit_test_domain():
    report = build_domain_report([_c(["tests/test_foo.py"])])
    assert report.count_for("test") == 1
    assert report.unclassified == 0


def test_unclassified_incremented_for_unknown_files():
    report = build_domain_report([_c(["mystery/file.xyz"])])
    assert report.unclassified == 1
    assert report.total() == 1


def test_multiple_commits_different_domains():
    commits = [
        _c(["tests/test_a.py"]),
        _c(["docs/guide.md"]),
        _c(["tests/test_b.py"]),
    ]
    report = build_domain_report(commits)
    assert report.count_for("test") == 2
    assert report.count_for("docs") == 1


def test_top_returns_sorted_by_count():
    commits = [
        _c(["tests/a.py"]),
        _c(["tests/b.py"]),
        _c(["docs/readme.md"]),
    ]
    report = build_domain_report(commits)
    top = report.top(2)
    assert top[0].domain == "test"
    assert top[0].count == 2


def test_domain_report_dict_structure():
    commits = [_c(["tests/test_foo.py"]), _c(["unknown/path.txt"])]
    report = build_domain_report(commits)
    d = domain_report_dict(report)
    assert d["total"] == 2
    assert d["unclassified"] == 1
    assert isinstance(d["domains"], list)
    assert d["domains"][0]["domain"] == "test"
    assert d["domains"][0]["count"] == 1
