"""Edge-case tests for velocity trend."""
from datetime import datetime, timezone

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_velocity_trend import (
    CommitVelocityTrendReport,
    VelocityTrendEntry,
    build_velocity_trend,
)


def _c(author: str) -> GitCommit:
    return GitCommit(
        sha="cafebabe",
        author=author,
        date=datetime(2024, 6, 10, 14, 0, tzinfo=timezone.utc),
        subject="fix: edge case",
        files_changed=[],
    )


def test_multiple_empty_weeks_produce_zero_counts():
    report = build_velocity_trend([[], [], []])
    assert len(report) == 0


def test_author_appears_only_in_middle_week():
    report = build_velocity_trend([[_c("alice")], [_c("bob")], [_c("alice")]])
    bob = next(e for e in report.entries() if e.author == "bob")
    assert bob.weekly_counts == [1]


def test_latest_returns_zero_for_empty_counts():
    entry = VelocityTrendEntry(author="ghost", weekly_counts=[])
    assert entry.latest == 0


def test_trend_stable_for_empty_counts():
    entry = VelocityTrendEntry(author="ghost", weekly_counts=[])
    assert entry.trend == "stable"


def test_top_zero_returns_empty():
    report = build_velocity_trend([[_c("alice"), _c("bob")]])
    assert report.top(0) == []


def test_top_larger_than_entries_returns_all():
    report = build_velocity_trend([[_c("alice"), _c("bob")]])
    assert len(report.top(100)) == 2


def test_entries_sorted_by_latest_descending():
    report = build_velocity_trend(
        [[_c("alice")], [_c("bob"), _c("bob"), _c("bob")]]
    )
    entries = report.entries()
    assert entries[0].author == "bob"


def test_add_week_updates_existing_authors():
    report = CommitVelocityTrendReport()
    report.add_week([_c("alice"), _c("alice")])
    report.add_week([_c("alice")])
    alice = report.entries()[0]
    assert alice.weekly_counts == [2, 1]
    assert alice.trend == "down"
