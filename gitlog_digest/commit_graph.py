"""Builds a simple ASCII commit graph showing activity per day across repos."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit

MAX_BAR_WIDTH = 20


@dataclass
class GraphRow:
    day: date
    count: int

    def bar(self, max_count: int) -> str:
        if max_count == 0:
            return ""
        filled = round((self.count / max_count) * MAX_BAR_WIDTH)
        return "█" * filled

    def __str__(self) -> str:
        return f"{self.day}  {self.bar(self.count):.<{MAX_BAR_WIDTH}}  {self.count}"


@dataclass
class CommitGraph:
    rows: List[GraphRow] = field(default_factory=list)

    @property
    def max_count(self) -> int:
        return max((r.count for r in self.rows), default=0)

    @property
    def total(self) -> int:
        return sum(r.count for r in self.rows)

    @property
    def peak_day(self) -> date | None:
        if not self.rows:
            return None
        return max(self.rows, key=lambda r: r.count).day


def build_commit_graph(commits: Sequence[GitCommit]) -> CommitGraph:
    """Aggregate commits by date and return a CommitGraph sorted by day."""
    counts: Dict[date, int] = {}
    for commit in commits:
        day = commit.date.date()
        counts[day] = counts.get(day, 0) + 1
    rows = [GraphRow(day=d, count=c) for d, c in sorted(counts.items())]
    return CommitGraph(rows=rows)


def format_commit_graph(graph: CommitGraph, title: str = "Commit Activity") -> str:
    """Render a CommitGraph as a human-readable ASCII string."""
    if not graph.rows:
        return f"{title}\n  (no commits)\n"

    max_count = graph.max_count
    lines = [title, "-" * (len(title))]
    for row in graph.rows:
        bar = row.bar(max_count)
        lines.append(f"  {row.day}  {bar:<{MAX_BAR_WIDTH}}  {row.count}")
    lines.append(f"\n  Total: {graph.total}  |  Peak day: {graph.peak_day}")
    return "\n".join(lines) + "\n"
