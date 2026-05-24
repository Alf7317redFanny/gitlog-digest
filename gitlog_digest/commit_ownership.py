"""Track which authors have touched each file most frequently."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from gitlog_digest.git_reader import GitCommit


@dataclass
class OwnershipEntry:
    filepath: str
    owner: str
    owner_count: int
    total_commits: int

    @property
    def ownership_ratio(self) -> float:
        if self.total_commits == 0:
            return 0.0
        return self.owner_count / self.total_commits

    def __str__(self) -> str:
        pct = int(self.ownership_ratio * 100)
        return f"{self.filepath}: {self.owner} ({pct}%, {self.owner_count}/{self.total_commits})"


@dataclass
class CommitOwnershipReport:
    _file_author_counts: Dict[str, Dict[str, int]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(int))
    )

    def add_commit(self, commit: GitCommit) -> None:
        for filepath in commit.files_changed:
            self._file_author_counts[filepath][commit.author] += 1

    def total_files(self) -> int:
        return len(self._file_author_counts)

    def entry_for(self, filepath: str) -> Optional[OwnershipEntry]:
        counts = self._file_author_counts.get(filepath)
        if not counts:
            return None
        owner = max(counts, key=lambda a: counts[a])
        return OwnershipEntry(
            filepath=filepath,
            owner=owner,
            owner_count=counts[owner],
            total_commits=sum(counts.values()),
        )

    def top(self, n: int = 10) -> List[OwnershipEntry]:
        entries = [
            self.entry_for(fp)
            for fp in self._file_author_counts
            if self.entry_for(fp) is not None
        ]
        return sorted(entries, key=lambda e: e.total_commits, reverse=True)[:n]

    def contested_files(self, threshold: float = 0.6) -> List[OwnershipEntry]:
        """Files where no single author owns more than `threshold` of commits."""
        result = []
        for fp in self._file_author_counts:
            entry = self.entry_for(fp)
            if entry and entry.ownership_ratio < threshold:
                result.append(entry)
        return sorted(result, key=lambda e: e.ownership_ratio)


def build_ownership_report(commits: List[GitCommit]) -> CommitOwnershipReport:
    report = CommitOwnershipReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def format_ownership_report(report: CommitOwnershipReport, n: int = 10) -> str:
    lines = ["## File Ownership"]
    top = report.top(n)
    if not top:
        lines.append("  (no data)")
        return "\n".join(lines)
    for entry in top:
        lines.append(f"  {entry}")
    contested = report.contested_files()
    if contested:
        lines.append("\n### Contested Files")
        for entry in contested[:5]:
            lines.append(f"  {entry}")
    return "\n".join(lines)
