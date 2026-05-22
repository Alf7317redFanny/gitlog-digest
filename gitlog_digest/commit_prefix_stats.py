"""Tracks conventional-commit-style prefix usage across commits.

Counts how often each prefix (feat, fix, chore, docs, etc.) appears
in commit subjects, regardless of whether full conventional format
is used.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from gitlog_digest.git_reader import GitCommit

_KNOWN_PREFIXES = (
    "feat", "fix", "chore", "docs", "style", "refactor",
    "perf", "test", "build", "ci", "revert", "wip",
)


def _extract_prefix(subject: str) -> Optional[str]:
    """Return the lowercase prefix if the subject starts with one, else None."""
    lowered = subject.strip().lower()
    for prefix in _KNOWN_PREFIXES:
        if lowered.startswith(prefix + ":") or lowered.startswith(prefix + "("):
            return prefix
    return None


@dataclass
class PrefixEntry:
    prefix: str
    count: int

    def __str__(self) -> str:
        return f"{self.prefix}: {self.count}"


@dataclass
class CommitPrefixReport:
    _counts: Counter = field(default_factory=Counter, repr=False)

    def add_commit(self, commit: GitCommit) -> None:
        prefix = _extract_prefix(commit.subject)
        if prefix:
            self._counts[prefix] += 1

    @property
    def total(self) -> int:
        return sum(self._counts.values())

    @property
    def unprefixed(self) -> int:
        """Placeholder — caller must track total commits separately."""
        return 0

    def top(self, n: int = 5) -> List[PrefixEntry]:
        return [
            PrefixEntry(prefix=p, count=c)
            for p, c in self._counts.most_common(n)
        ]

    def as_dict(self) -> dict:
        return dict(self._counts.most_common())


def build_prefix_report(commits: Sequence[GitCommit]) -> CommitPrefixReport:
    report = CommitPrefixReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def format_prefix_report(report: CommitPrefixReport, title: str = "Commit Prefixes") -> str:
    lines = [f"## {title}", ""]
    entries = report.top()
    if not entries:
        lines.append("  (no conventional prefixes found)")
    else:
        for entry in entries:
            lines.append(f"  {entry.prefix:<12} {entry.count}")
    return "\n".join(lines)
