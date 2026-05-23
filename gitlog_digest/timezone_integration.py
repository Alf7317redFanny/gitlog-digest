"""Integration helpers: per-repo and combined timezone reports."""
from __future__ import annotations

from typing import Dict, List

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_timezone import (
    CommitTimezoneReport,
    build_timezone_report,
    format_timezone_report,
)


def reports_per_repo(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> Dict[str, CommitTimezoneReport]:
    """Return a timezone report for each repository."""
    return {repo: build_timezone_report(commits) for repo, commits in commits_by_repo.items()}


def combined_report(commits_by_repo: Dict[str, List[GitCommit]]) -> CommitTimezoneReport:
    """Merge commits from all repos into a single timezone report."""
    all_commits: List[GitCommit] = []
    for commits in commits_by_repo.values():
        all_commits.extend(commits)
    return build_timezone_report(all_commits)


def timezone_report_dict(report: CommitTimezoneReport) -> dict:
    """Serialisable representation of a timezone report."""
    return {
        "total_commits": report.total,
        "unique_offsets": len(report),
        "top_offsets": [
            {"offset": e.label, "count": e.count}
            for e in report.top()
        ],
    }


def format_all_timezone_reports(
    commits_by_repo: Dict[str, List[GitCommit]],
    top_n: int = 5,
) -> str:
    """Format per-repo and combined timezone sections as a single string."""
    per_repo = reports_per_repo(commits_by_repo)
    sections: List[str] = []
    for repo, rpt in per_repo.items():
        header = f"=== {repo} ==="
        sections.append(f"{header}\n{format_timezone_report(rpt, top_n)}")
    combined = combined_report(commits_by_repo)
    sections.append(f"=== Combined ===\n{format_timezone_report(combined, top_n)}")
    return "\n\n".join(sections)
