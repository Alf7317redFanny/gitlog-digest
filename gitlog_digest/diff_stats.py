"""Parse and summarise per-commit diff statistics (insertions / deletions)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from gitlog_digest.git_reader import GitCommit


@dataclass
class DiffStat:
    sha: str
    insertions: int = 0
    deletions: int = 0

    @property
    def net(self) -> int:
        return self.insertions - self.deletions

    @property
    def total_changes(self) -> int:
        return self.insertions + self.deletions


@dataclass
class DiffSummary:
    stats: List[DiffStat] = field(default_factory=list)

    @property
    def total_insertions(self) -> int:
        return sum(s.insertions for s in self.stats)

    @property
    def total_deletions(self) -> int:
        return sum(s.deletions for s in self.stats)

    @property
    def total_changes(self) -> int:
        return self.total_insertions + self.total_deletions

    @property
    def most_changed_commit(self) -> DiffStat | None:
        if not self.stats:
            return None
        return max(self.stats, key=lambda s: s.total_changes)


def fetch_diff_stat(sha: str, repo_path: Path) -> DiffStat:
    """Run git show --stat for a single commit and parse insertions/deletions."""
    result = subprocess.run(
        ["git", "show", "--stat", "--format=", sha],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    insertions = 0
    deletions = 0
    for line in result.stdout.splitlines():
        if "insertion" in line or "deletion" in line:
            parts = line.split(",")
            for part in parts:
                part = part.strip()
                if "insertion" in part:
                    insertions = int(part.split()[0])
                elif "deletion" in part:
                    deletions = int(part.split()[0])
    return DiffStat(sha=sha, insertions=insertions, deletions=deletions)


def compute_diff_summary(commits: List[GitCommit], repo_path: Path) -> DiffSummary:
    """Compute diff stats for a list of commits."""
    stats = [fetch_diff_stat(c.sha, repo_path) for c in commits]
    return DiffSummary(stats=stats)
