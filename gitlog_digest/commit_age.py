"""Analyse the age distribution of commits within a week."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit


@dataclass
class AgeBucket:
    """Commits grouped by how many days ago they were authored."""
    days_ago: int
    commits: List[GitCommit] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.commits)

    def __str__(self) -> str:
        label = "today" if self.days_ago == 0 else (
            "yesterday" if self.days_ago == 1 else f"{self.days_ago}d ago"
        )
        return f"{label}: {len(self.commits)} commit(s)"


@dataclass
class CommitAgeReport:
    """Full age distribution for a collection of commits."""
    buckets: Dict[int, AgeBucket] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(len(b) for b in self.buckets.values())

    @property
    def freshest_day(self) -> int:
        """Minimum days_ago value with at least one commit."""
        active = [d for d, b in self.buckets.items() if len(b) > 0]
        return min(active) if active else -1

    @property
    def stalest_day(self) -> int:
        """Maximum days_ago value with at least one commit."""
        active = [d for d, b in self.buckets.items() if len(b) > 0]
        return max(active) if active else -1


def build_age_report(
    commits: Sequence[GitCommit],
    reference_date: date | None = None,
) -> CommitAgeReport:
    """Group *commits* by how many calendar days before *reference_date* they landed."""
    today = reference_date or date.today()
    report = CommitAgeReport()
    for commit in commits:
        delta = (today - commit.date.date()).days
        days_ago = max(delta, 0)
        if days_ago not in report.buckets:
            report.buckets[days_ago] = AgeBucket(days_ago=days_ago)
        report.buckets[days_ago].commits.append(commit)
    return report


def format_age_report(report: CommitAgeReport) -> str:
    """Return a human-readable summary of the age report."""
    if report.total == 0:
        return "No commits found."
    lines = ["Commit age distribution:"]
    for days_ago in sorted(report.buckets):
        bucket = report.buckets[days_ago]
        if len(bucket) > 0:
            lines.append(f"  {bucket}")
    lines.append(f"Total: {report.total} commit(s)")
    return "\n".join(lines)
