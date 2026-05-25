"""Tracks whether commits are arriving at a steady, accelerating, or decelerating
rate across the week by comparing day-over-day deltas."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Sequence

from gitlog_digest.git_reader import GitCommit


@dataclass
class RibbonDay:
    day: date
    count: int
    delta: int  # change vs previous day (0 for first day)

    def __str__(self) -> str:
        sign = "+" if self.delta >= 0 else ""
        return f"{self.day}  {self.count:>3} commits  ({sign}{self.delta})"


@dataclass
class CommitRibbonReport:
    _days: List[RibbonDay] = field(default_factory=list)

    def add_commits(self, commits: Sequence[GitCommit]) -> None:
        counts: dict[date, int] = defaultdict(int)
        for c in commits:
            counts[c.date.date()].append  # noqa – just checking; use below
        counts_clean: dict[date, int] = defaultdict(int)
        for c in commits:
            counts_clean[c.date.date()] += 1
        sorted_days = sorted(counts_clean.keys())
        prev = 0
        for d in sorted_days:
            cnt = counts_clean[d]
            self._days.append(RibbonDay(day=d, count=cnt, delta=cnt - prev))
            prev = cnt

    @property
    def days(self) -> List[RibbonDay]:
        return list(self._days)

    @property
    def total(self) -> int:
        return sum(r.count for r in self._days)

    @property
    def trend(self) -> str:
        """Overall trend: 'accelerating', 'decelerating', or 'steady'."""
        if len(self._days) < 2:
            return "steady"
        deltas = [r.delta for r in self._days[1:]]
        positive = sum(1 for d in deltas if d > 0)
        negative = sum(1 for d in deltas if d < 0)
        if positive > negative:
            return "accelerating"
        if negative > positive:
            return "decelerating"
        return "steady"

    @property
    def peak_day(self) -> Optional[date]:
        if not self._days:
            return None
        return max(self._days, key=lambda r: r.count).day

    def format_report(self) -> str:
        if not self._days:
            return "No commits."
        lines = [f"Trend: {self.trend}  |  Peak: {self.peak_day}  |  Total: {self.total}"]
        for row in self._days:
            lines.append(f"  {row}")
        return "\n".join(lines)
