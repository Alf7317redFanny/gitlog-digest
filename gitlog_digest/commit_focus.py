"""Tracks which directories/modules receive the most commit attention."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Optional

from gitlog_digest.git_reader import GitCommit


def _top_dir(path: str) -> Optional[str]:
    """Return the top-level directory of a file path, or None for root files."""
    parts = path.replace("\\", "/").split("/")
    return parts[0] if len(parts) > 1 else None


@dataclass
class FocusEntry:
    directory: str
    commit_count: int = 0
    author_set: set = field(default_factory=set)

    @property
    def unique_authors(self) -> int:
        return len(self.author_set)

    def __str__(self) -> str:
        return (
            f"{self.directory}: {self.commit_count} commits "
            f"({self.unique_authors} author(s))"
        )


@dataclass
class CommitFocusReport:
    _entries: dict = field(default_factory=dict)

    def add_commit(self, commit: GitCommit) -> None:
        for path in commit.files_changed:
            top = _top_dir(path)
            if top is None:
                continue
            if top not in self._entries:
                self._entries[top] = FocusEntry(directory=top)
            self._entries[top].commit_count += 1
            self._entries[top].author_set.add(commit.author)

    def top(self, n: int = 10) -> List[FocusEntry]:
        return sorted(
            self._entries.values(),
            key=lambda e: e.commit_count,
            reverse=True,
        )[:n]

    @property
    def total_directories(self) -> int:
        return len(self._entries)

    def merge(self, other: "CommitFocusReport") -> "CommitFocusReport":
        result = CommitFocusReport()
        for d, e in self._entries.items():
            result._entries[d] = FocusEntry(
                directory=d,
                commit_count=e.commit_count,
                author_set=set(e.author_set),
            )
        for d, e in other._entries.items():
            if d in result._entries:
                result._entries[d].commit_count += e.commit_count
                result._entries[d].author_set |= e.author_set
            else:
                result._entries[d] = FocusEntry(
                    directory=d,
                    commit_count=e.commit_count,
                    author_set=set(e.author_set),
                )
        return result


def build_focus_report(commits: List[GitCommit]) -> CommitFocusReport:
    report = CommitFocusReport()
    for c in commits:
        report.add_commit(c)
    return report
