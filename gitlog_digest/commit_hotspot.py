"""Identify files that appear most frequently across commits (hotspots)."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from gitlog_digest.git_reader import GitCommit


@dataclass
class HotspotEntry:
    path: str
    count: int

    def __str__(self) -> str:
        return f"{self.path} ({self.count} commits)"


@dataclass
class CommitHotspotReport:
    _counter: Counter = field(default_factory=Counter, repr=False)

    def add_commit(self, commit: GitCommit) -> None:
        for f in commit.files_changed:
            self._counter[f] += 1

    def total_files(self) -> int:
        return len(self._counter)

    def top(self, n: int = 10) -> List[HotspotEntry]:
        return [
            HotspotEntry(path=path, count=count)
            for path, count in self._counter.most_common(n)
        ]

    def peak(self) -> Optional[HotspotEntry]:
        entries = self.top(1)
        return entries[0] if entries else None

    def __len__(self) -> int:
        return self.total_files()


def build_hotspot_report(commits: Iterable[GitCommit]) -> CommitHotspotReport:
    report = CommitHotspotReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def format_hotspot_report(report: CommitHotspotReport, top_n: int = 10) -> str:
    entries = report.top(top_n)
    if not entries:
        return "Hotspots: (none)"
    lines = ["Hotspots (most frequently changed files):"]
    for rank, entry in enumerate(entries, start=1):
        lines.append(f"  {rank:>2}. {entry}")
    return "\n".join(lines)
