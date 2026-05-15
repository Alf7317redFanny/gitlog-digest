"""Tracks commit velocity (commits per active day) for each author."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit


@dataclass
class AuthorVelocityEntry:
    author: str
    total_commits: int
    active_days: int

    @property
    def velocity(self) -> float:
        """Average commits per active day."""
        if self.active_days == 0:
            return 0.0
        return round(self.total_commits / self.active_days, 2)

    def __str__(self) -> str:
        return (
            f"{self.author}: {self.total_commits} commits over "
            f"{self.active_days} active day(s) "
            f"({self.velocity:.2f} commits/day)"
        )


@dataclass
class AuthorVelocityReport:
    entries: List[AuthorVelocityEntry] = field(default_factory=list)

    def top(self, n: int = 5) -> List[AuthorVelocityEntry]:
        return sorted(self.entries, key=lambda e: e.velocity, reverse=True)[:n]

    def __len__(self) -> int:
        return len(self.entries)


def compute_velocity(commits: Sequence[GitCommit]) -> AuthorVelocityReport:
    """Compute per-author velocity from a list of commits."""
    commit_counts: Dict[str, int] = defaultdict(int)
    active_days: Dict[str, set] = defaultdict(set)

    for commit in commits:
        author = commit.author
        commit_counts[author] += 1
        active_days[author].add(commit.date.date() if hasattr(commit.date, "date") else commit.date)

    entries = [
        AuthorVelocityEntry(
            author=author,
            total_commits=commit_counts[author],
            active_days=len(active_days[author]),
        )
        for author in commit_counts
    ]
    entries.sort(key=lambda e: e.velocity, reverse=True)
    return AuthorVelocityReport(entries=entries)


def format_velocity_report(report: AuthorVelocityReport, top_n: int = 10) -> str:
    """Render the velocity report as a human-readable string."""
    if not report.entries:
        return "Author Velocity\n  (no data)\n"

    lines = ["Author Velocity (commits per active day)"]
    for entry in report.top(top_n):
        lines.append(f"  {entry}")
    return "\n".join(lines) + "\n"
