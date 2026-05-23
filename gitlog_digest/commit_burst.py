"""Detect burst periods — days where commit volume spikes significantly above average."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from gitlog_digest.git_reader import GitCommit

_BURST_MULTIPLIER = 2.0  # day must be >= 2x average to qualify


@dataclass
class BurstDay:
    day: date
    count: int
    ratio: float  # count / average

    def __str__(self) -> str:
        return f"{self.day.isoformat()}  {self.count} commits  ({self.ratio:.1f}x avg)"


@dataclass
class CommitBurstReport:
    _bursts: List[BurstDay] = field(default_factory=list)
    average_daily: float = 0.0

    @property
    def bursts(self) -> List[BurstDay]:
        return sorted(self._bursts, key=lambda b: b.count, reverse=True)

    @property
    def total_burst_days(self) -> int:
        return len(self._bursts)

    @property
    def peak(self) -> Optional[BurstDay]:
        return self.bursts[0] if self._bursts else None


def build_burst_report(
    commits: List[GitCommit],
    multiplier: float = _BURST_MULTIPLIER,
) -> CommitBurstReport:
    if not commits:
        return CommitBurstReport()

    counts: dict[date, int] = defaultdict(int)
    for c in commits:
        counts[c.date.date()].append if False else None  # type: ignore
        counts[c.date.date()] += 1

    total = sum(counts.values())
    avg = total / len(counts)

    bursts = [
        BurstDay(day=d, count=n, ratio=n / avg)
        for d, n in counts.items()
        if n >= avg * multiplier
    ]

    return CommitBurstReport(_bursts=bursts, average_daily=round(avg, 2))


def format_burst_report(report: CommitBurstReport) -> str:
    lines = [f"Burst days (>= {_BURST_MULTIPLIER}x avg of {report.average_daily:.1f}):\n"]
    if not report.bursts:
        lines.append("  (none)")
    else:
        for b in report.bursts:
            lines.append(f"  {b}")
    return "\n".join(lines)
