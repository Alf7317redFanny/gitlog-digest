"""Integration helpers: velocity reports per repo and combined."""
from __future__ import annotations

from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.author_velocity import (
    AuthorVelocityReport,
    compute_velocity,
    format_velocity_report,
)


def velocity_per_repo(
    repo_commits: Dict[str, Sequence[GitCommit]],
) -> Dict[str, AuthorVelocityReport]:
    """Return a velocity report keyed by repo name."""
    return {repo: compute_velocity(commits) for repo, commits in repo_commits.items()}


def combined_velocity(
    repo_commits: Dict[str, Sequence[GitCommit]],
) -> AuthorVelocityReport:
    """Merge all commits across repos into a single velocity report."""
    all_commits: List[GitCommit] = []
    for commits in repo_commits.values():
        all_commits.extend(commits)
    return compute_velocity(all_commits)


def velocity_report_dict(
    repo_commits: Dict[str, Sequence[GitCommit]],
) -> dict:
    """Serialisable summary of velocity data for all repos."""
    per_repo = velocity_per_repo(repo_commits)
    combined = combined_velocity(repo_commits)
    return {
        "per_repo": {
            repo: [
                {
                    "author": e.author,
                    "total_commits": e.total_commits,
                    "active_days": e.active_days,
                    "velocity": e.velocity,
                }
                for e in report.entries
            ]
            for repo, report in per_repo.items()
        },
        "combined": [
            {
                "author": e.author,
                "total_commits": e.total_commits,
                "active_days": e.active_days,
                "velocity": e.velocity,
            }
            for e in combined.entries
        ],
    }


def format_all_velocity_reports(
    repo_commits: Dict[str, Sequence[GitCommit]],
    top_n: int = 10,
) -> str:
    """Format velocity reports for every repo plus a combined section."""
    sections: List[str] = []
    for repo, report in velocity_per_repo(repo_commits).items():
        sections.append(f"[{repo}]\n{format_velocity_report(report, top_n)}")
    combined = combined_velocity(repo_commits)
    sections.append(f"[combined]\n{format_velocity_report(combined, top_n)}")
    return "\n".join(sections)
