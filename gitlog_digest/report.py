"""Combine filtering and stats to produce a per-repo report."""

from dataclasses import dataclass, field
from typing import List, Optional

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.filters import CommitFilter, apply_filter
from gitlog_digest.stats import CommitStats, compute_stats, most_active_day


@dataclass
class RepoReport:
    """Filtered + annotated report for a single repository."""
    repo_name: str
    commits: List[GitCommit]
    stats: CommitStats
    active_day: str
    applied_filter: Optional[CommitFilter] = field(default=None, repr=False)


def build_report(
    repo_name: str,
    commits: List[GitCommit],
    commit_filter: Optional[CommitFilter] = None,
) -> RepoReport:
    """Apply an optional filter then compute stats for *repo_name*."""
    filtered = apply_filter(commits, commit_filter) if commit_filter else commits
    stats = compute_stats(filtered)
    return RepoReport(
        repo_name=repo_name,
        commits=filtered,
        stats=stats,
        active_day=most_active_day(stats),
        applied_filter=commit_filter,
    )


def summarise_report(report: RepoReport) -> str:
    """Return a short human-readable summary string for the report."""
    s = report.stats
    if s.total == 0:
        return f"{report.repo_name}: no commits"
    lines = [
        f"{report.repo_name}: {s.total} commit(s) by {s.unique_authors} author(s)",
        f"  top contributor : {s.top_author} ({s.by_author[s.top_author]} commits)",
    ]
    if report.active_day:
        lines.append(f"  most active day : {report.active_day}")
    return "\n".join(lines)
