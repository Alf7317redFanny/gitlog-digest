"""Detect files that are frequently changed together (commit coupling)."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from typing import Iterable

from gitlog_digest.git_reader import GitCommit


@dataclass
class CouplingPair:
    file_a: str
    file_b: str
    count: int

    def __str__(self) -> str:
        return f"{self.file_a} <-> {self.file_b} ({self.count}x)"


@dataclass
class CommitCouplingReport:
    _pairs: dict[tuple[str, str], int] = field(default_factory=dict)

    def add_commit(self, commit: GitCommit) -> None:
        files = sorted(set(commit.files_changed))
        for a, b in combinations(files, 2):
            key = (a, b)
            self._pairs[key] = self._pairs.get(key, 0) + 1

    def top(self, n: int = 10) -> list[CouplingPair]:
        sorted_pairs = sorted(self._pairs.items(), key=lambda x: x[1], reverse=True)
        return [CouplingPair(a, b, count) for (a, b), count in sorted_pairs[:n]]

    def total_pairs(self) -> int:
        return len(self._pairs)

    def __len__(self) -> int:
        return self.total_pairs()


def build_coupling_report(commits: Iterable[GitCommit]) -> CommitCouplingReport:
    report = CommitCouplingReport()
    for commit in commits:
        if len(commit.files_changed) >= 2:
            report.add_commit(commit)
    return report


def format_coupling_report(report: CommitCouplingReport, n: int = 10) -> str:
    pairs = report.top(n)
    if not pairs:
        return "No file coupling data available."
    lines = ["File Coupling:", ""]
    for rank, pair in enumerate(pairs, 1):
        lines.append(f"  {rank:>2}. {pair}")
    return "\n".join(lines)
