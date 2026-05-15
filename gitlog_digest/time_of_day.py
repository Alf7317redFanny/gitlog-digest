"""Analyse commit activity by time of day (morning, afternoon, evening, night)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from gitlog_digest.git_reader import GitCommit

# Hour boundaries (24-hour clock)
_BUCKETS: list[tuple[str, range]] = [
    ("night",     range(0, 6)),
    ("morning",   range(6, 12)),
    ("afternoon", range(12, 18)),
    ("evening",   range(18, 24)),
]


def _bucket_for(hour: int) -> str:
    for name, rng in _BUCKETS:
        if hour in rng:
            return name
    return "unknown"


@dataclass
class TimeOfDayReport:
    counts: dict[str, int] = field(
        default_factory=lambda: {name: 0 for name, _ in _BUCKETS}
    )

    @property
    def total(self) -> int:
        return sum(self.counts.values())

    @property
    def peak_period(self) -> str | None:
        if self.total == 0:
            return None
        return max(self.counts, key=lambda k: self.counts[k])

    def __len__(self) -> int:
        return self.total


def build_time_of_day_report(commits: Iterable[GitCommit]) -> TimeOfDayReport:
    """Count commits per time-of-day bucket."""
    report = TimeOfDayReport()
    for commit in commits:
        bucket = _bucket_for(commit.date.hour)
        report.counts[bucket] = report.counts.get(bucket, 0) + 1
    return report


def format_time_of_day_report(report: TimeOfDayReport) -> str:
    """Return a short human-readable summary of commit timing."""
    if report.total == 0:
        return "No commits."
    lines = ["Commits by time of day:"]
    for name, _ in _BUCKETS:
        count = report.counts.get(name, 0)
        pct = (count / report.total * 100) if report.total else 0
        lines.append(f"  {name:<10} {count:>4}  ({pct:5.1f}%)")
    lines.append(f"  peak: {report.peak_period}")
    return "\n".join(lines)
