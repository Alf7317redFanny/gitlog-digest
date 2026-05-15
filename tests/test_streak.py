"""Tests for gitlog_digest.streak."""

from datetime import date, datetime
from types import SimpleNamespace

from gitlog_digest.streak import (
    compute_streaks,
    format_streak_report,
    _compute_streak,
    _commit_days_by_author,
)


def _c(author: str, day: date):
    return SimpleNamespace(author=author, date=datetime(day.year, day.month, day.day))


# ---------------------------------------------------------------------------
# _commit_days_by_author
# ---------------------------------------------------------------------------

def test_days_grouped_by_author():
    commits = [
        _c("Alice", date(2024, 1, 1)),
        _c("Alice", date(2024, 1, 2)),
        _c("Bob", date(2024, 1, 1)),
    ]
    result = _commit_days_by_author(commits)
    assert set(result["Alice"]) == {date(2024, 1, 1), date(2024, 1, 2)}
    assert result["Bob"] == [date(2024, 1, 1)]


def test_duplicate_days_deduplicated():
    commits = [
        _c("Alice", date(2024, 1, 5)),
        _c("Alice", date(2024, 1, 5)),
    ]
    result = _commit_days_by_author(commits)
    assert len(result["Alice"]) == 1


# ---------------------------------------------------------------------------
# _compute_streak
# ---------------------------------------------------------------------------

def test_single_day_streak():
    assert _compute_streak([date(2024, 1, 1)]) == (1, 1)


def test_consecutive_days():
    days = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
    current, longest = _compute_streak(days)
    assert current == 3
    assert longest == 3


def test_broken_streak():
    days = [
        date(2024, 1, 1), date(2024, 1, 2),  # streak of 2
        date(2024, 1, 5), date(2024, 1, 6), date(2024, 1, 7),  # streak of 3
    ]
    current, longest = _compute_streak(days)
    assert longest == 3
    assert current == 3


def test_current_streak_not_ending_on_last_run():
    # gap before last two days
    days = [
        date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3),
        date(2024, 1, 10), date(2024, 1, 11),
    ]
    current, longest = _compute_streak(days)
    assert longest == 3
    assert current == 2


# ---------------------------------------------------------------------------
# compute_streaks
# ---------------------------------------------------------------------------

def test_compute_streaks_returns_one_per_author():
    commits = [
        _c("Alice", date(2024, 1, 1)),
        _c("Bob", date(2024, 1, 2)),
    ]
    streaks = compute_streaks(commits)
    authors = {s.author for s in streaks}
    assert authors == {"Alice", "Bob"}


def test_compute_streaks_sorted_by_longest_desc():
    commits = [
        _c("Alice", date(2024, 1, 1)),
        _c("Bob", date(2024, 1, 1)),
        _c("Bob", date(2024, 1, 2)),
        _c("Bob", date(2024, 1, 3)),
    ]
    streaks = compute_streaks(commits)
    assert streaks[0].author == "Bob"


def test_active_days_count():
    commits = [
        _c("Alice", date(2024, 1, 1)),
        _c("Alice", date(2024, 1, 3)),
        _c("Alice", date(2024, 1, 5)),
    ]
    streaks = compute_streaks(commits)
    assert streaks[0].active_days == 3


# ---------------------------------------------------------------------------
# format_streak_report
# ---------------------------------------------------------------------------

def test_format_empty_streaks():
    out = format_streak_report([])
    assert "No streak data" in out


def test_format_contains_author():
    commits = [_c("Carol", date(2024, 3, 1))]
    streaks = compute_streaks(commits)
    out = format_streak_report(streaks)
    assert "Carol" in out
    assert "Commit Streaks" in out
