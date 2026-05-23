"""Tracks revert commits and the commits they revert."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from gitlog_digest.git_reader import GitCommit

_REVERT_RE = re.compile(r'revert\s+["\']?(.+?)["\']?$', re.IGNORECASE)
_THIS_REVERTS_RE = re.compile(r'This reverts commit ([0-9a-f]{7,40})', re.IGNORECASE)


def _extract_reverted_subject(subject: str) -> Optional[str]:
    m = _REVERT_RE.match(subject.strip())
    return m.group(1).strip('"\' ') if m else None


def _extract_reverted_sha(body: str) -> Optional[str]:
    m = _THIS_REVERTS_RE.search(body or "")
    return m.group(1)[:7] if m else None


@dataclass
class RevertEntry:
    sha: str
    author: str
    subject: str
    reverted_subject: Optional[str]
    reverted_sha: Optional[str]

    def __str__(self) -> str:
        target = self.reverted_subject or self.reverted_sha or "unknown"
        return f"{self.sha} by {self.author}: reverts '{target}'"


@dataclass
class CommitRevertReport:
    _entries: List[RevertEntry] = field(default_factory=list)

    def add_commit(self, commit: GitCommit) -> None:
        subject = commit.subject or ""
        if not subject.lower().startswith("revert"):
            return
        reverted_subject = _extract_reverted_subject(subject)
        reverted_sha = _extract_reverted_sha(getattr(commit, "body", "") or "")
        self._entries.append(
            RevertEntry(
                sha=commit.short_sha,
                author=commit.author,
                subject=subject,
                reverted_subject=reverted_subject,
                reverted_sha=reverted_sha,
            )
        )

    @property
    def total(self) -> int:
        return len(self._entries)

    def entries(self) -> List[RevertEntry]:
        return list(self._entries)

    def top(self, n: int = 5) -> List[RevertEntry]:
        return self._entries[:n]


def build_revert_report(commits: List[GitCommit]) -> CommitRevertReport:
    report = CommitRevertReport()
    for c in commits:
        report.add_commit(c)
    return report


def format_revert_report(report: CommitRevertReport) -> str:
    if report.total == 0:
        return "Reverts: none\n"
    lines = [f"Reverts ({report.total} total):"]
    for e in report.entries():
        lines.append(f"  {e}")
    return "\n".join(lines) + "\n"
