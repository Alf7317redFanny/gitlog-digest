"""Commit complexity scoring based on files changed, insertions, and deletions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from gitlog_digest.git_reader import GitCommit


_LOW_THRESHOLD = 10
_MEDIUM_THRESHOLD = 50


def _score(insertions: int, deletions: int, files: int) -> int:
    """Simple additive complexity score."""
    return insertions + deletions + files * 2


def _label(score: int) -> str:
    if score < _LOW_THRESHOLD:
        return "trivial"
    if score < _MEDIUM_THRESHOLD:
        return "moderate"
    return "complex"


@dataclass
class ComplexityEntry:
    sha: str
    author: str
    subject: str
    score: int
    label: str

    def __str__(self) -> str:
        return f"{self.sha[:7]}  [{self.label:8s}]  score={self.score}  {self.subject}"


@dataclass
class CommitComplexityReport:
    _entries: List[ComplexityEntry] = field(default_factory=list)

    def add_commit(
        self,
        commit: GitCommit,
        insertions: int = 0,
        deletions: int = 0,
        files_changed: int = 0,
    ) -> None:
        s = _score(insertions, deletions, files_changed)
        self._entries.append(
            ComplexityEntry(
                sha=commit.sha,
                author=commit.author,
                subject=commit.subject,
                score=s,
                label=_label(s),
            )
        )

    def total(self) -> int:
        return len(self._entries)

    def average_score(self) -> float:
        if not self._entries:
            return 0.0
        return sum(e.score for e in self._entries) / len(self._entries)

    def top(self, n: int = 5) -> List[ComplexityEntry]:
        return sorted(self._entries, key=lambda e: e.score, reverse=True)[:n]

    def by_label(self, label: str) -> List[ComplexityEntry]:
        return [e for e in self._entries if e.label == label]

    def entries(self) -> List[ComplexityEntry]:
        return list(self._entries)
