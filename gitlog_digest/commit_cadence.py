"""Measures the regularity/cadence of commits over time per author."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from statistics import stdev
from typing import Dict, List, Optional, Sequence

from gitlog_digest.git_reader import GitCommit


@dataclass
class CadenceEntry:
    author: str
    commit_days: List[date] = field(default_factory=list)

    @property
    def total_active_days(self) -> int:
        return len(set(self.commit_days))

    @property
    def gaps(self) -> List[int]:
        """Sorted list of day-gaps between consecutive active days."""
        days = sorted(set(self.commit_days))
        if len(days) < 2:
            return []
        return [(days[i + 1] - days[i]).days for i in range(len(days) - 1)]

    @property
    def average_gap(self) -> Optional[float]:
        g = self.gaps
        return sum(g) / len(g) if g else None

    @property
    def regularity_score(self) -> Optional[float]:
        """Lower stdev of gaps means more regular cadence. Returns None if < 2 gaps."""
        g = self.gaps
        if len(g) < 2:
            return None
        return round(stdev(g), 2)

    def __str__(self) -> str:
        avg = f"{self.average_gap:.1f}d" if self.average_gap is not None else "n/a"
        reg = f"{self.regularity_score:.2f}" if self.regularity_score is not None else "n/a"
        return f"{self.author}: active_days={self.total_active_days}, avg_gap={avg}, stdev={reg}"


@dataclass
class CommitCadenceReport:
    _entries: Dict[str, CadenceEntry] = field(default_factory=dict)

    def add_commit(self, commit: GitCommit) -> None:
        author = commit.author
        if author not in self._entries:
            self._entries[author] = CadenceEntry(author=author)
        self._entries[author].commit_days.append(commit.date.date())

    def entries(self) -> List[CadenceEntry]:
        return sorted(self._entries.values(), key=lambda e: e.total_active_days, reverse=True)

    def most_regular(self) -> Optional[CadenceEntry]:
        scored = [e for e in self._entries.values() if e.regularity_score is not None]
        if not scored:
            return None
        return min(scored, key=lambda e: e.regularity_score)  # type: ignore[arg-type]

    @property
    def total(self) -> int:
        return len(self._entries)


def build_cadence_report(commits: Sequence[GitCommit]) -> CommitCadenceReport:
    report = CommitCadenceReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def format_cadence_report(report: CommitCadenceReport, top_n: int = 5) -> str:
    lines = ["## Commit Cadence"]
    entries = report.entries()[:top_n]
    if not entries:
        lines.append("  No data.")
        return "\n".join(lines)
    for entry in entries:
        lines.append(f"  {entry}")
    most_reg = report.most_regular()
    if most_reg:
        lines.append(f"  Most regular: {most_reg.author} (stdev={most_reg.regularity_score}d)")
    return "\n".join(lines)
