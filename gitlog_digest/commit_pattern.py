"""Analyse recurring patterns in commit message prefixes over time."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional

from gitlog_digest.git_reader import GitCommit

_KNOWN_TYPES = {"feat", "fix", "chore", "docs", "refactor", "test", "style", "perf", "ci", "build"}


def _commit_type(subject: str) -> Optional[str]:
    """Return the conventional-commit type prefix, or None."""
    lower = subject.strip().lower()
    for t in _KNOWN_TYPES:
        if lower.startswith(t + ":") or lower.startswith(t + "("):
            return t
    return None


@dataclass
class PatternEntry:
    commit_type: str
    dates: List[date] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.dates)

    @property
    def peak_day(self) -> Optional[date]:
        if not self.dates:
            return None
        from collections import Counter
        return Counter(self.dates).most_common(1)[0][0]

    def __str__(self) -> str:
        return f"{self.commit_type}: {self.count} commits"


@dataclass
class CommitPatternReport:
    _entries: Dict[str, PatternEntry] = field(default_factory=dict)

    def add_commit(self, commit: GitCommit) -> None:
        ctype = _commit_type(commit.subject)
        if ctype is None:
            return
        if ctype not in self._entries:
            self._entries[ctype] = PatternEntry(commit_type=ctype)
        self._entries[ctype].dates.append(commit.date.date())

    @property
    def total(self) -> int:
        return sum(e.count for e in self._entries.values())

    @property
    def top_type(self) -> Optional[str]:
        if not self._entries:
            return None
        return max(self._entries, key=lambda k: self._entries[k].count)

    def sorted_entries(self) -> List[PatternEntry]:
        return sorted(self._entries.values(), key=lambda e: e.count, reverse=True)

    def __len__(self) -> int:
        return len(self._entries)


def build_pattern_report(commits: List[GitCommit]) -> CommitPatternReport:
    report = CommitPatternReport()
    for c in commits:
        report.add_commit(c)
    return report
