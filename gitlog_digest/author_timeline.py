"""Build a per-author commit timeline showing activity over a week."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit


@dataclass
class AuthorTimeline:
    """Maps each author to an ordered list of (date, commit_count) pairs."""

    entries: Dict[str, Dict[date, int]] = field(default_factory=dict)

    def dates_for(self, author: str) -> List[date]:
        """Return sorted dates on which *author* made commits."""
        return sorted(self.entries.get(author, {}).keys())

    def count_on(self, author: str, day: date) -> int:
        """Return the number of commits *author* made on *day*."""
        return self.entries.get(author, {}).get(day, 0)

    @property
    def authors(self) -> List[str]:
        """Alphabetically sorted list of authors present in the timeline."""
        return sorted(self.entries.keys())

    @property
    def all_dates(self) -> List[date]:
        """Sorted union of all dates across all authors."""
        days: set[date] = set()
        for counts in self.entries.values():
            days.update(counts.keys())
        return sorted(days)


def build_author_timeline(commits: Sequence[GitCommit]) -> AuthorTimeline:
    """Aggregate *commits* into an :class:`AuthorTimeline`."""
    raw: Dict[str, Dict[date, int]] = defaultdict(lambda: defaultdict(int))
    for commit in commits:
        day = commit.date.date() if hasattr(commit.date, "date") else commit.date
        raw[commit.author][day] += 1
    return AuthorTimeline(entries={author: dict(days) for author, days in raw.items()})


def format_author_timeline(timeline: AuthorTimeline) -> str:
    """Return a human-readable text table of the author timeline."""
    if not timeline.authors:
        return "No commits found."

    all_dates = timeline.all_dates
    date_headers = "  ".join(d.strftime("%a %d") for d in all_dates)
    col_width = 8
    header = f"{'Author':<20}  {date_headers}"
    lines = [header, "-" * len(header)]

    for author in timeline.authors:
        counts = "  ".join(
            str(timeline.count_on(author, d)).center(col_width) for d in all_dates
        )
        lines.append(f"{author:<20}  {counts}")

    return "\n".join(lines)
