"""Classify commits by label based on subject-line conventions."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import defaultdict
from typing import List, Dict, Optional

from gitlog_digest.git_reader import GitCommit

_LABEL_PREFIXES: Dict[str, str] = {
    "feat": "Feature",
    "fix": "Bug Fix",
    "docs": "Documentation",
    "style": "Style",
    "refactor": "Refactor",
    "perf": "Performance",
    "test": "Test",
    "chore": "Chore",
    "ci": "CI",
    "build": "Build",
    "revert": "Revert",
}


def _detect_label(subject: str) -> str:
    """Return a human-readable label for the commit subject, or 'Other'."""
    lower = subject.lower().strip()
    for prefix, label in _LABEL_PREFIXES.items():
        if lower.startswith(prefix + ":") or lower.startswith(prefix + "("):
            return label
    return "Other"


@dataclass
class LabelEntry:
    label: str
    count: int = 0
    commits: List[GitCommit] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.label}: {self.count} commit(s)"


@dataclass
class CommitLabelReport:
    _entries: Dict[str, LabelEntry] = field(default_factory=dict)

    def add_commit(self, commit: GitCommit) -> None:
        label = _detect_label(commit.subject)
        if label not in self._entries:
            self._entries[label] = LabelEntry(label=label)
        self._entries[label].count += 1
        self._entries[label].commits.append(commit)

    def total(self) -> int:
        return sum(e.count for e in self._entries.values())

    def labels(self) -> List[str]:
        return sorted(self._entries.keys())

    def entry_for(self, label: str) -> Optional[LabelEntry]:
        return self._entries.get(label)

    def top(self, n: int = 5) -> List[LabelEntry]:
        sorted_entries = sorted(
            self._entries.values(), key=lambda e: e.count, reverse=True
        )
        return sorted_entries[:n]

    def as_dict(self) -> Dict[str, int]:
        return {label: e.count for label, e in self._entries.items()}


def build_label_report(commits: List[GitCommit]) -> CommitLabelReport:
    report = CommitLabelReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def format_label_report(report: CommitLabelReport) -> str:
    if report.total() == 0:
        return "No commits to label."
    lines = ["Commit Labels:", "-" * 30]
    for entry in report.top(n=len(report.labels())):
        lines.append(f"  {entry.label:<20} {entry.count:>4}")
    return "\n".join(lines)
