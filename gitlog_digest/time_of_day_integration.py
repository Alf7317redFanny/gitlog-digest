"""Integration helpers: build and report time-of-day stats across multiple repos."""

from __future__ import annotations

from typing import Iterable, Mapping

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.time_of_day import (
    TimeOfDayReport,
    build_time_of_day_report,
    format_time_of_day_report,
)


def reports_per_repo(
    repo_commits: Mapping[str, Iterable[GitCommit]],
) -> dict[str, TimeOfDayReport]:
    """Return a TimeOfDayReport for each repository."""
    return {repo: build_time_of_day_report(commits) for repo, commits in repo_commits.items()}


def combined_report(reports: Mapping[str, TimeOfDayReport]) -> TimeOfDayReport:
    """Merge multiple per-repo reports into one aggregate report."""
    merged = TimeOfDayReport()
    for report in reports.values():
        for bucket, count in report.counts.items():
            merged.counts[bucket] = merged.counts.get(bucket, 0) + count
    return merged


def time_of_day_report_dict(report: TimeOfDayReport) -> dict:
    """Serialisable dict representation of a TimeOfDayReport."""
    return {
        "total": report.total,
        "peak_period": report.peak_period,
        "counts": dict(report.counts),
    }


def format_all_time_of_day_reports(
    repo_commits: Mapping[str, Iterable[GitCommit]],
    *,
    include_combined: bool = True,
) -> str:
    """Render a text block covering per-repo and optionally combined timing stats."""
    per_repo = reports_per_repo(repo_commits)
    sections: list[str] = []

    for repo_name, report in per_repo.items():
        sections.append(f"## {repo_name}")
        sections.append(format_time_of_day_report(report))

    if include_combined and len(per_repo) > 1:
        agg = combined_report(per_repo)
        sections.append("## Combined")
        sections.append(format_time_of_day_report(agg))

    return "\n\n".join(sections)
