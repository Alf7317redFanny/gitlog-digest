"""Tracks which directories/scopes are touched most frequently across commits."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Iterable, List, Tuple

from gitlog_digest.git_reader import GitCommit


def _top_level_scope(path: str) -> str:
    """Return the top-level directory of a file path, or '.' for root files."""
    parts = PurePosixPath(path).parts
    return parts[0] if len(parts) > 1 else "."


@dataclass
class ScopeEntry:
    scope: str
    file_count: int = 0
    commit_count: int = 0

    def __str__(self) -> str:
        return f"{self.scope}: {self.commit_count} commits, {self.file_count} files"


@dataclass
class CommitScopeReport:
    _scopes: dict[str, ScopeEntry] = field(default_factory=dict)

    def add_commit(self, commit: GitCommit) -> None:
        touched: dict[str, int] = defaultdict(int)
        for path in commit.files_changed:
            scope = _top_level_scope(path)
            touched[scope] += 1
        for scope, count in touched.items():
            if scope not in self._scopes:
                self._scopes[scope] = ScopeEntry(scope=scope)
            self._scopes[scope].file_count += count
            self._scopes[scope].commit_count += 1

    def scopes(self) -> List[ScopeEntry]:
        return sorted(self._scopes.values(), key=lambda e: e.commit_count, reverse=True)

    def top(self, n: int = 5) -> List[ScopeEntry]:
        return self.scopes()[:n]

    def __len__(self) -> int:
        return len(self._scopes)

    @property
    def total_files(self) -> int:
        return sum(e.file_count for e in self._scopes.values())


def build_scope_report(commits: Iterable[GitCommit]) -> CommitScopeReport:
    report = CommitScopeReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def scope_report_dict(report: CommitScopeReport) -> dict:
    return {
        "total_scopes": len(report),
        "total_files": report.total_files,
        "scopes": [
            {"scope": e.scope, "commit_count": e.commit_count, "file_count": e.file_count}
            for e in report.scopes()
        ],
    }


def format_scope_report(report: CommitScopeReport, top_n: int = 5) -> str:
    if not report:
        return "No scope data available."
    lines = ["## Commit Scope Breakdown", ""]
    for entry in report.top(top_n):
        lines.append(f"  {entry}")
    lines.append(f"\nTotal scopes touched: {len(report)}")
    return "\n".join(lines)
