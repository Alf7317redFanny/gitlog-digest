"""Tracks how long-lived commits are by measuring the span between
the first and last commit date per author across a set of commits."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional

from gitlog_digest.git_reader import GitCommit


@dataclass
class LongevityEntry:
    author: str
    first_date: date
    last_date: date
    commit_count: int

    @property
    def span_days(self) -> int:
        return (self.last_date - self.first_date).days

    def __str__(self) -> str:
        return (
            f"{self.author}: {self.commit_count} commits over {self.span_days} days"
            f" ({self.first_date} → {self.last_date})"
        )


@dataclass
class CommitLongevityReport:
    _entries: Dict[str, LongevityEntry] = field(default_factory=dict)

    def add_commit(self, commit: GitCommit) -> None:
        author = commit.author
        d = commit.date.date() if hasattr(commit.date, "date") else commit.date
        if author not in self._entries:
            self._entries[author] = LongevityEntry(
                author=author,
                first_date=d,
                last_date=d,
                commit_count=1,
            )
        else:
            entry = self._entries[author]
            entry.first_date = min(entry.first_date, d)
            entry.last_date = max(entry.last_date, d)
            entry.commit_count += 1

    def entries(self) -> List[LongevityEntry]:
        return sorted(self._entries.values(), key=lambda e: e.span_days, reverse=True)

    def total_authors(self) -> int:
        return len(self._entries)

    def top(self, n: int = 5) -> List[LongevityEntry]:
        return self.entries()[:n]

    def longest_span(self) -> Optional[LongevityEntry]:
        entries = self.entries()
        return entries[0] if entries else None


def build_longevity_report(commits: List[GitCommit]) -> CommitLongevityReport:
    report = CommitLongevityReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def format_longevity_report(report: CommitLongevityReport, top_n: int = 5) -> str:
    lines = ["## Commit Longevity"]
    entries = report.top(top_n)
    if not entries:
        lines.append("  No data.")
        return "\n".join(lines)
    for entry in entries:
        lines.append(f"  {entry}")
    return "\n".join(lines)
