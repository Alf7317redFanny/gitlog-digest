"""Tracks files that appear most frequently across commits (churn analysis)."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Tuple

from gitlog_digest.git_reader import GitCommit


@dataclass
class ChurnEntry:
    filepath: str
    count: int

    def __str__(self) -> str:
        return f"{self.filepath} ({self.count} commits)"


@dataclass
class CommitChurnReport:
    _counter: Counter = field(default_factory=Counter, repr=False)

    def add_commit(self, commit: GitCommit) -> None:
        for filepath in commit.files_changed:
            self._counter[filepath] += 1

    @property
    def total_files(self) -> int:
        return len(self._counter)

    @property
    def total_touches(self) -> int:
        return sum(self._counter.values())

    def top(self, n: int = 10) -> List[ChurnEntry]:
        return [
            ChurnEntry(filepath=fp, count=c)
            for fp, c in self._counter.most_common(n)
        ]

    def __len__(self) -> int:
        return self.total_files


def build_churn_report(commits: List[GitCommit]) -> CommitChurnReport:
    report = CommitChurnReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def format_churn_report(report: CommitChurnReport, top_n: int = 10) -> str:
    if not report.total_files:
        return "No file churn data available."

    lines = ["## File Churn", f"Total files touched: {report.total_files}"]
    lines.append("")
    lines.append("Most frequently changed files:")
    for entry in report.top(top_n):
        lines.append(f"  {entry}")
    return "\n".join(lines)


def churn_report_dict(report: CommitChurnReport, top_n: int = 10) -> dict:
    return {
        "total_files": report.total_files,
        "total_touches": report.total_touches,
        "top_files": [
            {"filepath": e.filepath, "count": e.count}
            for e in report.top(top_n)
        ],
    }
