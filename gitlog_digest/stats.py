"""Compute summary statistics from a list of GitCommit objects."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from gitlog_digest.git_reader import GitCommit


@dataclass
class CommitStats:
    total: int = 0
    by_author: dict[str, int] = field(default_factory=dict)
    unique_authors: set[str] = field(default_factory=set)
    top_author: Optional[str] = None
    by_day: dict[date, int] = field(default_factory=dict)
    most_active_day: Optional[str] = None


def compute_stats(commits: list[GitCommit]) -> CommitStats:
    """Compute statistics for a list of commits."""
    if not commits:
        return CommitStats()

    author_counter: Counter[str] = Counter()
    day_counter: Counter[date] = Counter()

    for commit in commits:
        author_counter[commit.author] += 1
        day_counter[commit.date] += 1

    top_author = author_counter.most_common(1)[0][0] if author_counter else None
    top_day = day_counter.most_common(1)[0][0] if day_counter else None

    return CommitStats(
        total=len(commits),
        by_author=dict(author_counter),
        unique_authors=set(author_counter.keys()),
        top_author=top_author,
        by_day=dict(day_counter),
        most_active_day=top_day.strftime("%A, %b %d") if top_day else None,
    )


def most_active_day(stats: CommitStats) -> Optional[str]:
    """Return a human-readable string for the most active day, or None."""
    return stats.most_active_day
