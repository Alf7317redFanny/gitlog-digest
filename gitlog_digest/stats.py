"""Compute simple statistics over a list of GitCommit objects."""

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict
from gitlog_digest.git_reader import GitCommit


@dataclass
class CommitStats:
    """Aggregated statistics for a collection of commits."""
    total: int = 0
    by_author: Dict[str, int] = field(default_factory=dict)
    by_date: Dict[str, int] = field(default_factory=dict)
    top_author: str = ""
    unique_authors: int = 0


def compute_stats(commits: List[GitCommit]) -> CommitStats:
    """Compute statistics from a list of commits."""
    if not commits:
        return CommitStats()

    by_author: Counter = Counter()
    by_date: Counter = Counter()

    for commit in commits:
        by_author[commit.author] += 1
        # date is expected as ISO-format string; use first 10 chars (YYYY-MM-DD)
        day = commit.date[:10]
        by_date[day] += 1

    top_author = by_author.most_common(1)[0][0]

    return CommitStats(
        total=len(commits),
        by_author=dict(by_author),
        by_date=dict(by_date),
        top_author=top_author,
        unique_authors=len(by_author),
    )


def most_active_day(stats: CommitStats) -> str:
    """Return the calendar date with the most commits, or empty string."""
    if not stats.by_date:
        return ""
    return max(stats.by_date, key=lambda d: stats.by_date[d])
