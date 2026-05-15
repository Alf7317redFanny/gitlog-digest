"""Analyse commit message lengths across repositories."""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, median
from typing import List, Sequence

from gitlog_digest.git_reader import GitCommit


@dataclass
class MessageLengthReport:
    """Statistics about commit subject line lengths."""
    lengths: List[int] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.lengths)

    @property
    def average(self) -> float:
        return round(mean(self.lengths), 1) if self.lengths else 0.0

    @property
    def median_length(self) -> float:
        return float(median(self.lengths)) if self.lengths else 0.0

    @property
    def shortest(self) -> int:
        return min(self.lengths) if self.lengths else 0

    @property
    def longest(self) -> int:
        return max(self.lengths) if self.lengths else 0

    @property
    def over_72(self) -> int:
        """Count of messages exceeding the conventional 72-char limit."""
        return sum(1 for l in self.lengths if l > 72)

    def __len__(self) -> int:
        return self.total


def build_message_length_report(
    commits: Sequence[GitCommit],
) -> MessageLengthReport:
    """Build a MessageLengthReport from a sequence of commits."""
    lengths = [len(c.subject.strip()) for c in commits if c.subject.strip()]
    return MessageLengthReport(lengths=lengths)


def format_message_length_report(report: MessageLengthReport) -> str:
    """Return a human-readable summary of message length statistics."""
    if report.total == 0:
        return "Message lengths: no commits."

    lines = [
        "Commit message lengths:",
        f"  Total commits : {report.total}",
        f"  Average length: {report.average} chars",
        f"  Median length : {report.median_length} chars",
        f"  Shortest      : {report.shortest} chars",
        f"  Longest       : {report.longest} chars",
        f"  Over 72 chars : {report.over_72}",
    ]
    return "\n".join(lines)


def message_length_report_dict(report: MessageLengthReport) -> dict:
    """Serialise report to a plain dict suitable for JSON export."""
    return {
        "total": report.total,
        "average": report.average,
        "median": report.median_length,
        "shortest": report.shortest,
        "longest": report.longest,
        "over_72": report.over_72,
    }
