"""Edge-case tests for CommitMomentumReport and MomentumEntry."""
import pytest
from datetime import datetime

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_momentum import (
    CommitMomentumReport,
    MomentumEntry,
    build_momentum_report,
    format_momentum_report,
)


def _c(author: str) -> GitCommit:
    return GitCommit(
        sha="cafebabe",
        short_sha="cafebab",
        author=author,
        date=datetime(2024, 6, 1, 12, 0),
        subject="docs: readme",
        files_changed=[],
        insertions=0,
        deletions=0,
        branch="main",
    )


def test_add_overwrites_existing_author():
    report = CommitMomentumReport()
    report.add("alice", 5, 3)
    report.add("alice", 7, 4)
    assert len(report) == 1
    assert report.entries()[0].current_count == 7


def test_ratio_when_previous_is_zero():
    entry = MomentumEntry(author="new", current_count=4, previous_count=0)
    assert entry.ratio == 4.0


def test_ratio_normal_case():
    entry = MomentumEntry(author="x", current_count=6, previous_count=3)
    assert entry.ratio == pytest.approx(2.0)


def test_multiple_authors_total_delta():
    current = [_c("a"), _c("a"), _c("b")]
    previous = [_c("a"), _c("b"), _c("b"), _c("b")]
    report = build_momentum_report(current, previous)
    # a: +1, b: -2 => total -1
    assert report.total_delta == -1
    assert report.overall_trend == "down"


def test_format_respects_top_n():
    current = {a: [_c(a)] * (i + 1) for i, a in enumerate("abcdefghij")}
    previous = {}
    all_current = [c for commits in current.values() for c in commits]
    report = build_momentum_report(all_current, [])
    text = format_momentum_report(report, top_n=3)
    # Only top 3 authors should appear in body lines
    body_lines = [l for l in text.splitlines() if l.startswith("  ")]
    assert len(body_lines) == 3


def test_entry_str_negative_delta():
    entry = MomentumEntry(author="bob", current_count=1, previous_count=5)
    s = str(entry)
    assert "-4" in s
    assert "down" in s


def test_entry_str_flat_delta():
    entry = MomentumEntry(author="carol", current_count=3, previous_count=3)
    s = str(entry)
    assert "+0" in s
    assert "flat" in s
