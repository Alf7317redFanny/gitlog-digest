"""Generates a simple text-based activity heatmap showing commit frequency by day of week."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict

from gitlog_digest.git_reader import GitCommit

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
BARS = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]


@dataclass
class ActivityHeatmap:
    """Commit counts bucketed by day-of-week (0=Mon … 6=Sun)."""

    counts: Dict[int, int] = field(default_factory=lambda: {i: 0 for i in range(7)})

    @property
    def total(self) -> int:
        return sum(self.counts.values())

    @property
    def peak_day(self) -> str:
        """Name of the day with the most commits."""
        if self.total == 0:
            return "N/A"
        idx = max(self.counts, key=lambda k: self.counts[k])
        return DAYS[idx]


def build_heatmap(commits: List[GitCommit]) -> ActivityHeatmap:
    """Build an ActivityHeatmap from a list of commits."""
    heatmap = ActivityHeatmap()
    counter: Counter = Counter()
    for commit in commits:
        dow = commit.date.weekday()  # 0=Monday
        counter[dow] += 1
    for dow, count in counter.items():
        heatmap.counts[dow] = count
    return heatmap


def _bar(value: int, max_value: int) -> str:
    if max_value == 0:
        return BARS[0]
    idx = round(value / max_value * (len(BARS) - 1))
    return BARS[idx]


def format_heatmap(heatmap: ActivityHeatmap) -> str:
    """Render the heatmap as a compact text block."""
    if heatmap.total == 0:
        return "Activity heatmap: no commits"

    max_count = max(heatmap.counts.values())
    lines = ["Activity by day-of-week:"]
    for i, day in enumerate(DAYS):
        count = heatmap.counts[i]
        bar = _bar(count, max_count)
        lines.append(f"  {day}  {bar}  {count}")
    lines.append(f"  Peak day: {heatmap.peak_day}")
    return "\n".join(lines)
