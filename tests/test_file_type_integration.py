"""Integration tests for file type stats across multiple repos."""

import pytest
from datetime import date
from gitlog_digest.git_reader import GitCommit
from gitlog_digest.file_type_stats import FileTypeReport, build_file_type_report


def _c(sha, author, files):
    """Helper to build a GitCommit with a list of changed filenames."""
    return GitCommit(
        sha=sha,
        author=author,
        date=date(2024, 3, 11),
        subject="some commit",
        files=files,
    )


# ---------------------------------------------------------------------------
# Multi-repo aggregation
# ---------------------------------------------------------------------------

def test_multi_repo_reports_are_independent():
    """Each repo should produce its own FileTypeReport without bleed-over."""
    repo_a_commits = [
        _c("aaa", "Alice", ["main.py", "utils.py"]),
        _c("bbb", "Alice", ["README.md"]),
    ]
    repo_b_commits = [
        _c("ccc", "Bob", ["index.js", "app.js"]),
        _c("ddd", "Bob", ["styles.css"]),
    ]

    report_a = build_file_type_report(repo_a_commits)
    report_b = build_file_type_report(repo_b_commits)

    assert ".py" in report_a.extensions
    assert ".md" in report_a.extensions
    assert ".js" not in report_a.extensions

    assert ".js" in report_b.extensions
    assert ".css" in report_b.extensions
    assert ".py" not in report_b.extensions


def test_combined_report_merges_extensions():
    """Merging two reports should sum counts for shared extensions."""
    commits_a = [_c("a1", "Alice", ["foo.py", "bar.py"])]
    commits_b = [_c("b1", "Bob", ["baz.py", "qux.ts"])]

    report_a = build_file_type_report(commits_a)
    report_b = build_file_type_report(commits_b)
    combined = report_a.merge(report_b)

    py_entry = combined.entry_for(".py")
    assert py_entry is not None
    assert py_entry.count == 3  # 2 from a + 1 from b

    ts_entry = combined.entry_for(".ts")
    assert ts_entry is not None
    assert ts_entry.count == 1


def test_combined_report_top_extension():
    """Top extension in the combined report should reflect merged counts."""
    commits_a = [_c("a1", "Alice", ["a.py", "b.py", "c.py"])]
    commits_b = [_c("b1", "Bob", ["d.py", "e.js"])]

    combined = build_file_type_report(commits_a).merge(build_file_type_report(commits_b))
    top = combined.top(1)

    assert len(top) == 1
    assert top[0].extension == ".py"
    assert top[0].count == 4


def test_empty_repo_merge_does_not_affect_other():
    """Merging an empty report should leave the original unchanged."""
    commits = [_c("x1", "Alice", ["main.go", "server.go"])]
    report = build_file_type_report(commits)
    empty = build_file_type_report([])

    merged = report.merge(empty)

    assert ".go" in merged.extensions
    assert merged.entry_for(".go").count == 2


def test_no_extension_files_tracked_separately():
    """Files without extensions should be counted under a placeholder key."""
    commits = [_c("y1", "Carol", ["Makefile", "Dockerfile", "main.py"])]
    report = build_file_type_report(commits)

    # Files without dots should still be counted
    total_files = sum(e.count for e in report.top(len(report.extensions)))
    assert total_files == 3


def test_top_n_limits_results():
    """top(n) should return at most n entries, sorted by count descending."""
    commits = [
        _c("z1", "Dave", ["a.py", "b.py", "c.py"]),
        _c("z2", "Dave", ["d.js", "e.js"]),
        _c("z3", "Dave", ["f.ts"]),
    ]
    report = build_file_type_report(commits)
    top2 = report.top(2)

    assert len(top2) == 2
    assert top2[0].count >= top2[1].count
    assert top2[0].extension == ".py"
