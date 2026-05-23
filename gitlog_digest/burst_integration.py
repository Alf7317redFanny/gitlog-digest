"""Integration helpers: build burst reports per-repo and combined."""
from __future__ import annotations

from typing import Dict, List

from gitlog_digest.commit_burst import (
    CommitBurstReport,
    build_burst_report,
    format_burst_report,
)
from gitlog_digest.git_reader import GitCommit


def bursts_per_repo(
    repo_commits: Dict[str, List[GitCommit]],
) -> Dict[str, CommitBurstReport]:
    """Return a burst report keyed by repo name."""
    return {repo: build_burst_report(commits) for repo, commits in repo_commits.items()}


def combined_burst(repo_commits: Dict[str, List[GitCommit]]) -> CommitBurstReport:
    """Merge all commits across repos into a single burst report."""
    all_commits: List[GitCommit] = []
    for commits in repo_commits.values():
        all_commits.extend(commits)
    return build_burst_report(all_commits)


def burst_report_dict(report: CommitBurstReport) -> dict:
    return {
        "average_daily": report.average_daily,
        "total_burst_days": report.total_burst_days,
        "peak": (
            {
                "day": report.peak.day.isoformat(),
                "count": report.peak.count,
                "ratio": round(report.peak.ratio, 2),
            }
            if report.peak
            else None
        ),
        "bursts": [
            {
                "day": b.day.isoformat(),
                "count": b.count,
                "ratio": round(b.ratio, 2),
            }
            for b in report.bursts
        ],
    }


def format_all_burst_reports(
    repo_commits: Dict[str, List[GitCommit]],
) -> str:
    """Return a formatted string covering every repo plus a combined section."""
    sections: List[str] = []
    per_repo = bursts_per_repo(repo_commits)
    for repo, report in per_repo.items():
        sections.append(f"=== {repo} ===")
        sections.append(format_burst_report(report))
    if len(per_repo) > 1:
        sections.append("=== combined ===")
        sections.append(format_burst_report(combined_burst(repo_commits)))
    return "\n".join(sections)
