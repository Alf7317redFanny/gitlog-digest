"""Track which branches saw commit activity during the digest period."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit


@dataclass
class BranchEntry:
    branch: str
    commit_count: int
    authors: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        author_str = ", ".join(sorted(set(self.authors)))
        return f"{self.branch}: {self.commit_count} commit(s) by {author_str}"


@dataclass
class BranchActivityReport:
    _entries: Dict[str, BranchEntry] = field(default_factory=dict)

    def add_commit(self, branch: str, commit: GitCommit) -> None:
        if branch not in self._entries:
            self._entries[branch] = BranchEntry(branch=branch, commit_count=0)
        entry = self._entries[branch]
        entry.commit_count += 1
        entry.authors.append(commit.author)

    @property
    def branches(self) -> List[BranchEntry]:
        return sorted(
            self._entries.values(),
            key=lambda e: e.commit_count,
            reverse=True,
        )

    @property
    def total(self) -> int:
        return sum(e.commit_count for e in self._entries.values())

    @property
    def most_active(self) -> BranchEntry | None:
        return self.branches[0] if self.branches else None

    def __len__(self) -> int:
        return len(self._entries)


def build_branch_report(
    commits_by_branch: Dict[str, Sequence[GitCommit]],
) -> BranchActivityReport:
    """Build a BranchActivityReport from a mapping of branch -> commits."""
    report = BranchActivityReport()
    for branch, commits in commits_by_branch.items():
        for commit in commits:
            report.add_commit(branch, commit)
    return report


def format_branch_report(report: BranchActivityReport) -> str:
    """Return a human-readable text summary of branch activity."""
    if not report.branches:
        return "No branch activity recorded."

    lines = ["Branch Activity:", ""]
    for entry in report.branches:
        unique_authors = sorted(set(entry.authors))
        lines.append(
            f"  {entry.branch}: {entry.commit_count} commit(s) "
            f"({', '.join(unique_authors)})"
        )
    lines.append("")
    lines.append(f"Total branches active: {len(report)}")
    if report.most_active:
        lines.append(f"Most active branch: {report.most_active.branch}")
    return "\n".join(lines)
