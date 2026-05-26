"""Tracks co-authorship patterns — pairs of authors who commit to the same files."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from typing import List, Tuple

from gitlog_digest.git_reader import GitCommit


@dataclass
class CollabPair:
    author_a: str
    author_b: str
    shared_files: int

    def __str__(self) -> str:
        return f"{self.author_a} <-> {self.author_b}: {self.shared_files} shared file(s)"


@dataclass
class CommitCollabReport:
    _file_authors: dict = field(default_factory=lambda: defaultdict(set), repr=False)
    _pair_counts: dict = field(default_factory=lambda: defaultdict(int), repr=False)

    def add_commit(self, commit: GitCommit) -> None:
        for f in commit.files:
            self._file_authors[f].add(commit.author)

    def build(self) -> None:
        """Compute pair counts from accumulated file-author data."""
        self._pair_counts.clear()
        for authors in self._file_authors.values():
            for a, b in combinations(sorted(authors), 2):
                self._pair_counts[(a, b)] += 1

    def top(self, n: int = 5) -> List[CollabPair]:
        self.build()
        ranked = sorted(self._pair_counts.items(), key=lambda x: x[1], reverse=True)
        return [CollabPair(a, b, count) for (a, b), count in ranked[:n]]

    def total_pairs(self) -> int:
        self.build()
        return len(self._pair_counts)

    def __len__(self) -> int:
        return self.total_pairs()


def build_collab_report(commits: List[GitCommit]) -> CommitCollabReport:
    report = CommitCollabReport()
    for commit in commits:
        report.add_commit(commit)
    report.build()
    return report


def format_collab_report(report: CommitCollabReport, n: int = 5) -> str:
    pairs = report.top(n)
    if not pairs:
        return "Co-authorship: no shared file activity found."
    lines = ["Co-authorship pairs (by shared files):"]
    for pair in pairs:
        lines.append(f"  {pair}")
    return "\n".join(lines)
