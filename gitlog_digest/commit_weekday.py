"""Analyse commit distribution across days of the week."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@dataclass
class WeekdayEntry:
    day_name: str
    day_index: int  # 0=Monday, 6=Sunday
    count: int

    def __str__(self) -> str:
        bar = "#" * self.count
        return f"{self.day_name:<10} {self.count:>4}  {bar}"


@dataclass
class CommitWeekdayReport:
    _counts: Counter = field(default_factory=Counter)

    def add_commit(self, commit) -> None:
        day_index = commit.date.weekday()  # 0=Monday
        self._counts[day_index] += 1

    @property
    def total(self) -> int:
        return sum(self._counts.values())

    @property
    def peak_day(self) -> Optional[str]:
        if not self._counts:
            return None
        idx = self._counts.most_common(1)[0][0]
        return DAY_NAMES[idx]

    @property
    def weekend_ratio(self) -> float:
        if self.total == 0:
            return 0.0
        weekend = self._counts[5] + self._counts[6]
        return weekend / self.total

    def entries(self) -> List[WeekdayEntry]:
        return [
            WeekdayEntry(day_name=DAY_NAMES[i], day_index=i, count=self._counts.get(i, 0))
            for i in range(7)
        ]


def build_weekday_report(commits) -> CommitWeekdayReport:
    report = CommitWeekdayReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def format_weekday_report(report: CommitWeekdayReport, title: str = "Commits by Day of Week") -> str:
    lines = [title, "-" * len(title)]
    for entry in report.entries():
        lines.append(str(entry))
    lines.append(f"\nTotal : {report.total}")
    if report.peak_day:
        lines.append(f"Peak  : {report.peak_day}")
    lines.append(f"Weekend ratio: {report.weekend_ratio:.1%}")
    return "\n".join(lines)


def weekday_report_dict(report: CommitWeekdayReport) -> dict:
    return {
        "total": report.total,
        "peak_day": report.peak_day,
        "weekend_ratio": round(report.weekend_ratio, 4),
        "by_day": {
            e.day_name: e.count for e in report.entries()
        },
    }
