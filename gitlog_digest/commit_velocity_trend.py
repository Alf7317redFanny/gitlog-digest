"""Tracks week-over-week velocity trend per author across a rolling window."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Sequence

from gitlog_digest.git_reader import GitCommit


@dataclass
class VelocityTrendEntry:
    author: str
    weekly_counts: List[int] = field(default_factory=list)

    @property
    def trend(self) -> str:
        if len(self.weekly_counts) < 2:
            return "stable"
        delta = self.weekly_counts[-1] - self.weekly_counts[-2]
        if delta > 0:
            return "up"
        if delta < 0:
            return "down"
        return "stable"

    @property
    def latest(self) -> int:
        return self.weekly_counts[-1] if self.weekly_counts else 0

    def __str__(self) -> str:
        arrow = {"up": "↑", "down": "↓", "stable": "→"}[self.trend]
        counts = ", ".join(str(c) for c in self.weekly_counts)
        return f"{self.author}: [{counts}] {arrow}"


@dataclass
class CommitVelocityTrendReport:
    _entries: Dict[str, VelocityTrendEntry] = field(default_factory=dict)

    def add_week(self, commits: Sequence[GitCommit]) -> None:
        seen: Dict[str, int] = defaultdict(int)
        for commit in commits:
            seen[commit.author] += 1
        for author, entry in self._entries.items():
            entry.weekly_counts.append(seen.get(author, 0))
        for author, count in seen.items():
            if author not in self._entries:
                self._entries[author] = VelocityTrendEntry(author=author, weekly_counts=[count])

    def entries(self) -> List[VelocityTrendEntry]:
        return sorted(self._entries.values(), key=lambda e: -e.latest)

    def top(self, n: int = 5) -> List[VelocityTrendEntry]:
        return self.entries()[:n]

    def __len__(self) -> int:
        return len(self._entries)


def build_velocity_trend(
    weekly_commit_lists: Sequence[Sequence[GitCommit]],
) -> CommitVelocityTrendReport:
    report = CommitVelocityTrendReport()
    for week_commits in weekly_commit_lists:
        report.add_week(week_commits)
    return report


def format_velocity_trend_report(report: CommitVelocityTrendReport, top_n: int = 5) -> str:
    entries = report.top(top_n)
    if not entries:
        return "Velocity Trend: no data\n"
    lines = ["Velocity Trend (weekly commits per author):"]
    for entry in entries:
        lines.append(f"  {entry}")
    return "\n".join(lines) + "\n"
