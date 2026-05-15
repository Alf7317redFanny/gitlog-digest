"""Analyse commit frequency patterns across a date range."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit


@dataclass
class FrequencyBucket:
    """Commit count for a single calendar date."""
    day: date
    count: int

    def __str__(self) -> str:
        return f"{self.day.isoformat()}: {self.count} commit{'s' if self.count != 1 else ''}"


@dataclass
class CommitFrequency:
    """Frequency distribution of commits over a set of dates."""
    buckets: List[FrequencyBucket] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(b.count for b in self.buckets)

    @property
    def peak(self) -> FrequencyBucket | None:
        return max(self.buckets, key=lambda b: b.count, default=None)

    @property
    def average(self) -> float:
        if not self.buckets:
            return 0.0
        active = [b for b in self.buckets if b.count > 0]
        if not active:
            return 0.0
        return self.total / len(active)

    def days_with_commits(self) -> int:
        return sum(1 for b in self.buckets if b.count > 0)


def build_frequency(commits: Sequence[GitCommit]) -> CommitFrequency:
    """Build a CommitFrequency from a sequence of commits."""
    counter: Counter[date] = Counter()
    for commit in commits:
        counter[commit.date.date()] += 1

    buckets = [
        FrequencyBucket(day=day, count=cnt)
        for day, cnt in sorted(counter.items())
    ]
    return CommitFrequency(buckets=buckets)


def format_frequency_report(freq: CommitFrequency) -> str:
    """Render a human-readable frequency report."""
    if not freq.buckets:
        return "No commits in range."

    lines: List[str] = ["Commit Frequency", "----------------"]
    for bucket in freq.buckets:
        lines.append(f"  {bucket}")

    lines.append("")
    lines.append(f"Total commits : {freq.total}")
    lines.append(f"Active days   : {freq.days_with_commits()}")
    lines.append(f"Average/day   : {freq.average:.1f}")
    if freq.peak:
        lines.append(f"Peak day      : {freq.peak.day.isoformat()} ({freq.peak.count} commits)")

    return "\n".join(lines)
