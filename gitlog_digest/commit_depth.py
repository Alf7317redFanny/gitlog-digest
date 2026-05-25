"""Measures the directory depth distribution of changed files across commits."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Optional

from gitlog_digest.git_reader import GitCommit


def _path_depth(path: str) -> int:
    """Return the number of directory levels in a file path (0 = root)."""
    parts = path.strip("/").split("/")
    return max(0, len(parts) - 1)


@dataclass
class DepthBucket:
    depth: int
    count: int = 0

    def __str__(self) -> str:  # pragma: no cover
        label = f"depth {self.depth}"
        return f"{label:<12} {self.count:>4} file(s)"


@dataclass
class CommitDepthReport:
    _buckets: dict = field(default_factory=dict)

    def add_commit(self, commit: GitCommit) -> None:
        for path in commit.changed_files:
            d = _path_depth(path)
            if d not in self._buckets:
                self._buckets[d] = DepthBucket(depth=d)
            self._buckets[d].count += 1

    def total(self) -> int:
        return sum(b.count for b in self._buckets.values())

    def buckets(self) -> List[DepthBucket]:
        return sorted(self._buckets.values(), key=lambda b: b.depth)

    def peak_depth(self) -> Optional[int]:
        if not self._buckets:
            return None
        return max(self._buckets.values(), key=lambda b: b.count).depth

    def average_depth(self) -> Optional[float]:
        if not self._buckets:
            return None
        total_files = self.total()
        if total_files == 0:
            return None
        weighted = sum(b.depth * b.count for b in self._buckets.values())
        return weighted / total_files

    def merge(self, other: "CommitDepthReport") -> "CommitDepthReport":
        merged = CommitDepthReport()
        for d, b in self._buckets.items():
            merged._buckets[d] = DepthBucket(depth=d, count=b.count)
        for d, b in other._buckets.items():
            if d in merged._buckets:
                merged._buckets[d].count += b.count
            else:
                merged._buckets[d] = DepthBucket(depth=d, count=b.count)
        return merged


def build_depth_report(commits: List[GitCommit]) -> CommitDepthReport:
    report = CommitDepthReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def format_depth_report(report: CommitDepthReport, title: str = "File Depth Distribution") -> str:
    lines = [title]
    if not report.buckets():
        lines.append("  (no data)")
        return "\n".join(lines)
    for bucket in report.buckets():
        lines.append(f"  {bucket}")
    avg = report.average_depth()
    if avg is not None:
        lines.append(f"  avg depth: {avg:.2f}")
    return "\n".join(lines)
