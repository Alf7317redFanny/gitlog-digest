"""Tracks the flow of commit types over time (additions vs deletions vs refactors)."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional

from gitlog_digest.git_reader import GitCommit

_FLOW_KEYWORDS = {
    "add": ["add", "feat", "new", "create", "introduce"],
    "remove": ["remove", "delete", "drop", "clean", "deprecate"],
    "refactor": ["refactor", "restructure", "reorganise", "reorganize", "rename", "move"],
    "fix": ["fix", "bug", "patch", "correct", "resolve"],
}


def _classify_flow(subject: str) -> str:
    lower = subject.lower()
    for label, keywords in _FLOW_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return label
    return "other"


@dataclass
class FlowEntry:
    day: date
    add: int = 0
    remove: int = 0
    refactor: int = 0
    fix: int = 0
    other: int = 0

    def increment(self, label: str) -> None:
        if hasattr(self, label):
            setattr(self, label, getattr(self, label) + 1)

    @property
    def total(self) -> int:
        return self.add + self.remove + self.refactor + self.fix + self.other

    def __str__(self) -> str:
        return (
            f"{self.day}  +{self.add} add  -{self.remove} rm  "
            f"~{self.refactor} ref  !{self.fix} fix  ?{self.other} other"
        )


@dataclass
class CommitFlowReport:
    _entries: Dict[date, FlowEntry] = field(default_factory=dict)

    def add_commit(self, commit: GitCommit) -> None:
        d = commit.date.date() if hasattr(commit.date, "date") else commit.date
        if d not in self._entries:
            self._entries[d] = FlowEntry(day=d)
        label = _classify_flow(commit.subject)
        self._entries[d].increment(label)

    def entries(self) -> List[FlowEntry]:
        return sorted(self._entries.values(), key=lambda e: e.day)

    @property
    def total(self) -> int:
        return sum(e.total for e in self._entries.values())

    def dominant_type(self) -> Optional[str]:
        totals: Dict[str, int] = defaultdict(int)
        for e in self._entries.values():
            for label in ("add", "remove", "refactor", "fix", "other"):
                totals[label] += getattr(e, label)
        if not totals:
            return None
        return max(totals, key=lambda k: totals[k])


def build_flow_report(commits: List[GitCommit]) -> CommitFlowReport:
    report = CommitFlowReport()
    for c in commits:
        report.add_commit(c)
    return report


def format_flow_report(report: CommitFlowReport, title: str = "Commit Flow") -> str:
    lines = [f"=== {title} ==="]
    if not report.entries():
        lines.append("  (no commits)")
        return "\n".join(lines)
    for entry in report.entries():
        lines.append(f"  {entry}")
    dom = report.dominant_type()
    if dom:
        lines.append(f"  dominant type: {dom}")
    return "\n".join(lines)
