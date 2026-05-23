"""Analyse commit activity by timezone offset."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from gitlog_digest.git_reader import GitCommit


def _offset_label(offset_minutes: int) -> str:
    """Return a human-readable UTC offset string like UTC+05:30."""
    sign = "+" if offset_minutes >= 0 else "-"
    abs_min = abs(offset_minutes)
    hours, mins = divmod(abs_min, 60)
    if mins:
        return f"UTC{sign}{hours:02d}:{mins:02d}"
    return f"UTC{sign}{hours:02d}"


@dataclass
class TimezoneEntry:
    offset_minutes: int
    count: int = 0

    @property
    def label(self) -> str:
        return _offset_label(self.offset_minutes)

    def __str__(self) -> str:
        return f"{self.label}: {self.count} commit{'s' if self.count != 1 else ''}"


@dataclass
class CommitTimezoneReport:
    _entries: Dict[int, TimezoneEntry] = field(default_factory=dict)

    def add_commit(self, commit: GitCommit) -> None:
        tz = commit.author_date.utcoffset()
        offset = int(tz.total_seconds() // 60) if tz is not None else 0
        if offset not in self._entries:
            self._entries[offset] = TimezoneEntry(offset_minutes=offset)
        self._entries[offset].count += 1

    @property
    def total(self) -> int:
        return sum(e.count for e in self._entries.values())

    @property
    def offsets(self) -> List[int]:
        return sorted(self._entries.keys())

    def entry_for(self, offset: int) -> Optional[TimezoneEntry]:
        return self._entries.get(offset)

    def top(self, n: int = 5) -> List[TimezoneEntry]:
        return sorted(self._entries.values(), key=lambda e: e.count, reverse=True)[:n]

    def __len__(self) -> int:
        return len(self._entries)


def build_timezone_report(commits: List[GitCommit]) -> CommitTimezoneReport:
    report = CommitTimezoneReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def format_timezone_report(report: CommitTimezoneReport, top_n: int = 5) -> str:
    if report.total == 0:
        return "Timezone activity: no commits."
    lines = ["Timezone activity:"]
    for entry in report.top(top_n):
        lines.append(f"  {entry}")
    return "\n".join(lines)
