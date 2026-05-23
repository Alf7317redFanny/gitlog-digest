"""Integration helpers for revert reports across multiple repos."""
from __future__ import annotations

from typing import Dict, List

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_revert import (
    CommitRevertReport,
    build_revert_report,
    format_revert_report,
)


def reverts_per_repo(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> Dict[str, CommitRevertReport]:
    """Return a revert report keyed by repo name."""
    return {repo: build_revert_report(commits) for repo, commits in commits_by_repo.items()}


def combined_revert(commits_by_repo: Dict[str, List[GitCommit]]) -> CommitRevertReport:
    """Merge all commits across repos into a single revert report."""
    all_commits: List[GitCommit] = []
    for commits in commits_by_repo.values():
        all_commits.extend(commits)
    return build_revert_report(all_commits)


def revert_report_dict(report: CommitRevertReport) -> dict:
    """Serialisable dict representation of a revert report."""
    return {
        "total_reverts": report.total,
        "entries": [
            {
                "sha": e.sha,
                "author": e.author,
                "subject": e.subject,
                "reverted_subject": e.reverted_subject,
                "reverted_sha": e.reverted_sha,
            }
            for e in report.entries()
        ],
    }


def format_all_revert_reports(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> str:
    """Format revert reports for all repos, followed by a combined summary."""
    parts: List[str] = []
    per_repo = reverts_per_repo(commits_by_repo)
    for repo, report in per_repo.items():
        parts.append(f"=== {repo} ===")
        parts.append(format_revert_report(report))
    combined = combined_revert(commits_by_repo)
    parts.append("=== combined ===")
    parts.append(format_revert_report(combined))
    return "\n".join(parts)
