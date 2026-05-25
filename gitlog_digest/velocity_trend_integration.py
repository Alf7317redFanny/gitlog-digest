"""Integration helpers for velocity trend across multiple repos."""
from __future__ import annotations

from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_velocity_trend import (
    CommitVelocityTrendReport,
    VelocityTrendEntry,
    build_velocity_trend,
    format_velocity_trend_report,
)


def trends_per_repo(
    repo_weekly_commits: Dict[str, Sequence[Sequence[GitCommit]]],
) -> Dict[str, CommitVelocityTrendReport]:
    """Build a velocity trend report for each repo."""
    return {
        repo: build_velocity_trend(weekly_lists)
        for repo, weekly_lists in repo_weekly_commits.items()
    }


def combined_trend(
    repo_weekly_commits: Dict[str, Sequence[Sequence[GitCommit]]],
) -> CommitVelocityTrendReport:
    """Merge all repos into a single trend report."""
    if not repo_weekly_commits:
        return CommitVelocityTrendReport()
    num_weeks = max(len(v) for v in repo_weekly_commits.values())
    merged: List[List[GitCommit]] = [[] for _ in range(num_weeks)]
    for weekly_lists in repo_weekly_commits.values():
        for i, week_commits in enumerate(weekly_lists):
            merged[i].extend(week_commits)
    return build_velocity_trend(merged)


def velocity_trend_report_dict(
    report: CommitVelocityTrendReport, top_n: int = 5
) -> dict:
    return {
        "top_authors": [
            {
                "author": e.author,
                "weekly_counts": e.weekly_counts,
                "trend": e.trend,
                "latest": e.latest,
            }
            for e in report.top(top_n)
        ],
        "total_tracked_authors": len(report),
    }


def format_all_velocity_trend_reports(
    repo_weekly_commits: Dict[str, Sequence[Sequence[GitCommit]]],
    top_n: int = 5,
) -> str:
    reports = trends_per_repo(repo_weekly_commits)
    sections = []
    for repo, report in sorted(reports.items()):
        header = f"=== {repo} ==="
        body = format_velocity_trend_report(report, top_n=top_n)
        sections.append(f"{header}\n{body}")
    return "\n".join(sections)
