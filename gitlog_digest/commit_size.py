"""Categorises commits by size based on lines changed (insertions + deletions)."""

from dataclasses import dataclass, field
from typing import List, Dict
from gitlog_digest.git_reader import GitCommit


# Size thresholds (total lines changed)
SMALL_MAX = 10
MEDIUM_MAX = 50
LARGE_MAX = 200


@dataclass
class SizeBucket:
    label: str
    min_lines: int
    max_lines: int  # inclusive; -1 means unbounded
    commits: List[GitCommit] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.commits)

    def __str__(self) -> str:
        if self.max_lines == -1:
            range_str = f"{self.min_lines}+ lines"
        else:
            range_str = f"{self.min_lines}–{self.max_lines} lines"
        return f"{self.label} ({range_str}): {len(self.commits)} commit(s)"


@dataclass
class CommitSizeReport:
    small: SizeBucket = field(default_factory=lambda: SizeBucket("small", 0, SMALL_MAX))
    medium: SizeBucket = field(default_factory=lambda: SizeBucket("medium", SMALL_MAX + 1, MEDIUM_MAX))
    large: SizeBucket = field(default_factory=lambda: SizeBucket("large", MEDIUM_MAX + 1, LARGE_MAX))
    xlarge: SizeBucket = field(default_factory=lambda: SizeBucket("xlarge", LARGE_MAX + 1, -1))

    @property
    def total(self) -> int:
        return len(self.small) + len(self.medium) + len(self.large) + len(self.xlarge)

    def buckets(self) -> List[SizeBucket]:
        return [self.small, self.medium, self.large, self.xlarge]

    def as_dict(self) -> Dict[str, int]:
        return {b.label: len(b) for b in self.buckets()}


def _lines_changed(commit: GitCommit) -> int:
    """Return total lines changed for a commit (insertions + deletions)."""
    return getattr(commit, "insertions", 0) + getattr(commit, "deletions", 0)


def build_size_report(commits: List[GitCommit]) -> CommitSizeReport:
    """Classify each commit into a size bucket and return the report."""
    report = CommitSizeReport()
    for commit in commits:
        total = _lines_changed(commit)
        if total <= SMALL_MAX:
            report.small.commits.append(commit)
        elif total <= MEDIUM_MAX:
            report.medium.commits.append(commit)
        elif total <= LARGE_MAX:
            report.large.commits.append(commit)
        else:
            report.xlarge.commits.append(commit)
    return report


def format_size_report(report: CommitSizeReport) -> str:
    """Return a human-readable summary of commit sizes."""
    lines = ["Commit size distribution:"]
    for bucket in report.buckets():
        lines.append(f"  {bucket}")
    return "\n".join(lines)
