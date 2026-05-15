"""Compute author commit streaks from a list of GitCommit objects."""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


@dataclass
class AuthorStreak:
    author: str
    current_streak: int  # consecutive days up to and including latest commit day
    longest_streak: int
    active_days: int
    latest_day: Optional[date] = None


def _commit_days_by_author(commits: list) -> Dict[str, List[date]]:
    """Return sorted list of unique commit dates per author."""
    mapping: Dict[str, set] = defaultdict(set)
    for c in commits:
        mapping[c.author].add(c.date.date() if hasattr(c.date, "date") else c.date)
    return {author: sorted(days) for author, days in mapping.items()}


def _compute_streak(days: List[date]) -> tuple:
    """Return (current_streak, longest_streak) for a sorted list of unique dates."""
    if not days:
        return 0, 0

    longest = 1
    current_run = 1

    for i in range(1, len(days)):
        if days[i] - days[i - 1] == timedelta(days=1):
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 1

    # current streak: how long the streak ending on the last day is
    current = 1
    for i in range(len(days) - 1, 0, -1):
        if days[i] - days[i - 1] == timedelta(days=1):
            current += 1
        else:
            break

    return current, longest


def compute_streaks(commits: list) -> List[AuthorStreak]:
    """Compute streak info for every author in the commit list."""
    by_author = _commit_days_by_author(commits)
    results: List[AuthorStreak] = []
    for author, days in by_author.items():
        current, longest = _compute_streak(days)
        results.append(
            AuthorStreak(
                author=author,
                current_streak=current,
                longest_streak=longest,
                active_days=len(days),
                latest_day=days[-1] if days else None,
            )
        )
    return sorted(results, key=lambda s: (-s.longest_streak, s.author))


def format_streak_report(streaks: List[AuthorStreak]) -> str:
    """Render streak data as a plain-text table."""
    if not streaks:
        return "No streak data available.\n"

    lines = ["## Commit Streaks", "",
             f"  {'Author':<20} {'Current':>8} {'Longest':>8} {'Active Days':>12}",
             "  " + "-" * 50]
    for s in streaks:
        lines.append(
            f"  {s.author:<20} {s.current_streak:>8} {s.longest_streak:>8} {s.active_days:>12}"
        )
    lines.append("")
    return "\n".join(lines)
