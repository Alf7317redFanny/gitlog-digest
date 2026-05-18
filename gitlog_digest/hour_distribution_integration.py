"""Integration helpers for hour-distribution reports across multiple repos."""
from __future__ import annotations

from typing import Dict, List

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_hour_distribution import (
    HourDistributionReport,
    build_hour_distribution,
    format_hour_distribution,
)


def distributions_per_repo(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> Dict[str, HourDistributionReport]:
    """Return an individual HourDistributionReport for each repo."""
    return {
        repo: build_hour_distribution(commits)
        for repo, commits in commits_by_repo.items()
    }


def combined_distribution(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> HourDistributionReport:
    """Merge all repo commits into a single distribution report."""
    all_commits: List[GitCommit] = []
    for commits in commits_by_repo.values():
        all_commits.extend(commits)
    return build_hour_distribution(all_commits)


def hour_distribution_report_dict(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> dict:
    """Return a serialisable dict summarising hour distributions."""
    combined = combined_distribution(commits_by_repo)
    per_repo = distributions_per_repo(commits_by_repo)
    return {
        "peak_hour": combined.peak_hour,
        "total_commits": combined.total,
        "by_hour": {
            f"{h:02d}": combined.count_for(h) for h in range(24)
        },
        "repos": {
            repo: {
                "peak_hour": r.peak_hour,
                "total_commits": r.total,
            }
            for repo, r in per_repo.items()
        },
    }


def format_all_hour_distribution_reports(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> str:
    """Render a text block with per-repo and combined hour distributions."""
    sections: List[str] = []
    per_repo = distributions_per_repo(commits_by_repo)
    for repo, report in per_repo.items():
        sections.append(f"=== {repo} ===")
        sections.append(format_hour_distribution(report))
    combined = combined_distribution(commits_by_repo)
    sections.append("=== Combined ===")
    sections.append(format_hour_distribution(combined))
    return "\n\n".join(sections)
