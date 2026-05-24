"""Tracks week-over-week commit momentum per author and overall."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit


@dataclass
class MomentumEntry:
    author: str
    current_count: int
    previous_count: int

    @property
    def delta(self) -> int:
        return self.current_count - self.previous_count

    @property
    def ratio(self) -> float:
        if self.previous_count == 0:
            return float(self.current_count)
        return self.current_count / self.previous_count

    @property
    def trend(self) -> str:
        if self.delta > 0:
            return "up"
        if self.delta < 0:
            return "down"
        return "flat"

    def __str__(self) -> str:
        sign = "+" if self.delta >= 0 else ""
        return (
            f"{self.author}: {self.current_count} commits "
            f"({sign}{self.delta}, {self.trend})"
        )


@dataclass
class CommitMomentumReport:
    _entries: Dict[str, MomentumEntry] = field(default_factory=dict)

    def add(self, author: str, current: int, previous: int) -> None:
        self._entries[author] = MomentumEntry(
            author=author, current_count=current, previous_count=previous
        )

    def entries(self) -> List[MomentumEntry]:
        return sorted(self._entries.values(), key=lambda e: e.delta, reverse=True)

    @property
    def total_delta(self) -> int:
        return sum(e.delta for e in self._entries.values())

    @property
    def overall_trend(self) -> str:
        if self.total_delta > 0:
            return "up"
        if self.total_delta < 0:
            return "down"
        return "flat"

    def __len__(self) -> int:
        return len(self._entries)


def build_momentum_report(
    current_commits: Sequence[GitCommit],
    previous_commits: Sequence[GitCommit],
) -> CommitMomentumReport:
    def _count_by_author(commits: Sequence[GitCommit]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for c in commits:
            counts[c.author] = counts.get(c.author, 0) + 1
        return counts

    current = _count_by_author(current_commits)
    previous = _count_by_author(previous_commits)
    all_authors = set(current) | set(previous)

    report = CommitMomentumReport()
    for author in all_authors:
        report.add(author, current.get(author, 0), previous.get(author, 0))
    return report


def format_momentum_report(report: CommitMomentumReport, top_n: int = 10) -> str:
    if not report.entries():
        return "No momentum data available."
    lines = [f"Commit Momentum (overall: {report.overall_trend}, delta {report.total_delta:+d})"]
    for entry in report.entries()[:top_n]:
        lines.append(f"  {entry}")
    return "\n".join(lines)
