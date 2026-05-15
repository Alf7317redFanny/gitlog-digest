"""Tracks authors who contributed in consecutive weeks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from gitlog_digest.git_reader import GitCommit


@dataclass
class RepeatAuthorReport:
    """Result of comparing author sets across two weeks."""

    returning: List[str] = field(default_factory=list)
    new_this_week: List[str] = field(default_factory=list)
    dropped_off: List[str] = field(default_factory=list)

    @property
    def returning_count(self) -> int:
        return len(self.returning)

    @property
    def new_count(self) -> int:
        return len(self.new_this_week)

    @property
    def dropped_count(self) -> int:
        return len(self.dropped_off)


def _author_set(commits: List[GitCommit]) -> Set[str]:
    return {c.author for c in commits}


def compare_author_sets(
    previous: List[GitCommit],
    current: List[GitCommit],
) -> RepeatAuthorReport:
    """Compare author participation between two weeks."""
    prev_authors = _author_set(previous)
    curr_authors = _author_set(current)

    returning = sorted(prev_authors & curr_authors)
    new_this_week = sorted(curr_authors - prev_authors)
    dropped_off = sorted(prev_authors - curr_authors)

    return RepeatAuthorReport(
        returning=returning,
        new_this_week=new_this_week,
        dropped_off=dropped_off,
    )


def format_repeat_author_report(report: RepeatAuthorReport) -> str:
    """Render a RepeatAuthorReport as a human-readable string."""
    lines: List[str] = ["## Author Retention"]

    if report.returning:
        lines.append(f"Returning ({report.returning_count}): {', '.join(report.returning)}")
    else:
        lines.append("Returning (0): —")

    if report.new_this_week:
        lines.append(f"New this week ({report.new_count}): {', '.join(report.new_this_week)}")
    else:
        lines.append("New this week (0): —")

    if report.dropped_off:
        lines.append(f"Dropped off ({report.dropped_count}): {', '.join(report.dropped_off)}")
    else:
        lines.append("Dropped off (0): —")

    return "\n".join(lines)


def repeat_author_dict(report: RepeatAuthorReport) -> Dict:
    """Serialise a RepeatAuthorReport to a plain dict."""
    return {
        "returning": report.returning,
        "new_this_week": report.new_this_week,
        "dropped_off": report.dropped_off,
        "returning_count": report.returning_count,
        "new_count": report.new_count,
        "dropped_count": report.dropped_count,
    }
