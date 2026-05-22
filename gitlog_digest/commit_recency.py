"""Tracks how recently commits were made, bucketing them by age relative to now."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Sequence

from gitlog_digest.git_reader import GitCommit

_BUCKETS = [
    (1, "Today"),
    (2, "Yesterday"),
    (7, "This week"),
    (30, "This month"),
    (90, "Last 3 months"),
]
_OLDER_LABEL = "Older"


def _bucket_label(days_ago: float) -> str:
    for threshold, label in _BUCKETS:
        if days_ago < threshold:
            return label
    for threshold, label in _BUCKETS:
        if days_ago <= threshold:
            return label
    # Check each threshold in order
    prev = 0
    for threshold, label in _BUCKETS:
        if days_ago <= threshold:
            return label
    return _OLDER_LABEL


@dataclass
class RecencyBucket:
    label: str
    count: int = 0

    def __str__(self) -> str:
        return f"{self.label}: {self.count} commit{'s' if self.count != 1 else ''}"


@dataclass
class CommitRecencyReport:
    buckets: List[RecencyBucket] = field(default_factory=list)
    _index: dict = field(default_factory=dict, repr=False)

    def add_commit(self, commit: GitCommit, now: datetime | None = None) -> None:
        if now is None:
            now = datetime.now(timezone.utc)
        ts = commit.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        days_ago = (now - ts).total_seconds() / 86400
        label = _bucket_label(days_ago)
        if label not in self._index:
            bucket = RecencyBucket(label=label)
            self.buckets.append(bucket)
            self._index[label] = bucket
        self._index[label].count += 1

    def total(self) -> int:
        return sum(b.count for b in self.buckets)

    def most_recent_bucket(self) -> str | None:
        order = [label for _, label in _BUCKETS] + [_OLDER_LABEL]
        for label in order:
            if label in self._index and self._index[label].count > 0:
                return label
        return None


def build_recency_report(
    commits: Sequence[GitCommit], now: datetime | None = None
) -> CommitRecencyReport:
    report = CommitRecencyReport()
    for commit in commits:
        report.add_commit(commit, now=now)
    return report


def format_recency_report(report: CommitRecencyReport) -> str:
    if not report.buckets:
        return "No commits."
    lines = ["Commit Recency:"] + [f"  {b}" for b in report.buckets]
    return "\n".join(lines)


def recency_report_dict(report: CommitRecencyReport) -> dict:
    return {
        "total": report.total(),
        "most_recent_bucket": report.most_recent_bucket(),
        "buckets": [{"label": b.label, "count": b.count} for b in report.buckets],
    }
