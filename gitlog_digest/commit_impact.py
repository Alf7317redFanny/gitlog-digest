"""Measures the relative impact of commits based on files changed and diff size."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from gitlog_digest.git_reader import GitCommit


def _impact_score(files_changed: int, insertions: int, deletions: int) -> float:
    """Compute a simple impact score: files * 2 + lines changed."""
    return files_changed * 2.0 + insertions + deletions


def _impact_label(score: float) -> str:
    if score == 0:
        return "none"
    if score < 10:
        return "minor"
    if score < 50:
        return "moderate"
    if score < 200:
        return "significant"
    return "major"


@dataclass
class ImpactEntry:
    sha: str
    author: str
    subject: str
    score: float
    label: str

    def __str__(self) -> str:
        return f"{self.sha[:7]}  [{self.label:>11}]  {self.subject}  (score={self.score:.1f})"


@dataclass
class CommitImpactReport:
    _entries: List[ImpactEntry] = field(default_factory=list)

    def add_commit(
        self,
        commit: GitCommit,
        files_changed: int = 0,
        insertions: int = 0,
        deletions: int = 0,
    ) -> None:
        score = _impact_score(files_changed, insertions, deletions)
        label = _impact_label(score)
        self._entries.append(
            ImpactEntry(
                sha=commit.sha,
                author=commit.author,
                subject=commit.subject,
                score=score,
                label=label,
            )
        )

    def total(self) -> int:
        return len(self._entries)

    def top(self, n: int = 5) -> List[ImpactEntry]:
        return sorted(self._entries, key=lambda e: e.score, reverse=True)[:n]

    def average_score(self) -> float:
        if not self._entries:
            return 0.0
        return sum(e.score for e in self._entries) / len(self._entries)

    def by_label(self) -> dict:
        counts: dict = {}
        for e in self._entries:
            counts[e.label] = counts.get(e.label, 0) + 1
        return counts

    def peak(self) -> Optional[ImpactEntry]:
        if not self._entries:
            return None
        return max(self._entries, key=lambda e: e.score)
