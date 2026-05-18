"""Analyse the distribution of commits by hour of the day (0-23)."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from gitlog_digest.git_reader import GitCommit


@dataclass
class HourBucket:
    hour: int
    count: int = 0

    def __str__(self) -> str:
        bar = "█" * self.count
        return f"{self.hour:02d}:00  {bar} ({self.count})"


@dataclass
class HourDistributionReport:
    _buckets: Dict[int, HourBucket] = field(default_factory=dict)

    def add_commit(self, commit: GitCommit) -> None:
        h = commit.date.hour
        if h not in self._buckets:
            self._buckets[h] = HourBucket(hour=h)
        self._buckets[h].count += 1

    @property
    def total(self) -> int:
        return sum(b.count for b in self._buckets.values())

    @property
    def peak_hour(self) -> Optional[int]:
        if not self._buckets:
            return None
        return max(self._buckets, key=lambda h: self._buckets[h].count)

    def count_for(self, hour: int) -> int:
        return self._buckets.get(hour, HourBucket(hour=hour)).count

    def sorted_buckets(self) -> List[HourBucket]:
        return [self._buckets[h] for h in sorted(self._buckets)]

    def __len__(self) -> int:
        return len(self._buckets)


def build_hour_distribution(commits: List[GitCommit]) -> HourDistributionReport:
    report = HourDistributionReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def format_hour_distribution(report: HourDistributionReport) -> str:
    if not report.total:
        return "No commits to display."
    lines = ["Commits by hour:", ""]
    for bucket in report.sorted_buckets():
        lines.append(str(bucket))
    if report.peak_hour is not None:
        lines.append(f"\nPeak hour: {report.peak_hour:02d}:00")
    return "\n".join(lines)
