"""Integration helpers for commit churn across multiple repositories."""

from __future__ import annotations

from typing import Dict, List

from .commit_churn import CommitChurnReport, build_churn_report
from .git_reader import GitCommit


def churn_per_repo(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> Dict[str, CommitChurnReport]:
    """Build a churn report for each repository.

    Args:
        commits_by_repo: Mapping of repo name to its list of commits.

    Returns:
        Mapping of repo name to its :class:`CommitChurnReport`.
    """
    return {
        repo: build_churn_report(commits)
        for repo, commits in commits_by_repo.items()
    }


def combined_churn(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> CommitChurnReport:
    """Merge churn data from all repositories into a single report.

    Args:
        commits_by_repo: Mapping of repo name to its list of commits.

    Returns:
        A :class:`CommitChurnReport` aggregating all repos.
    """
    all_commits: List[GitCommit] = [
        commit
        for commits in commits_by_repo.values()
        for commit in commits
    ]
    return build_churn_report(all_commits)


def churn_report_dict(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> dict:
    """Return a JSON-serialisable dict summarising churn across all repos.

    Keys:
        - ``per_repo``: dict mapping repo name -> list of {file, count} entries
        - ``combined``: list of {file, count} entries across all repos
        - ``total_files_touched``: unique file count across all repos

    Args:
        commits_by_repo: Mapping of repo name to its list of commits.
    """
    per = churn_per_repo(commits_by_repo)
    combined = combined_churn(commits_by_repo)

    return {
        "per_repo": {
            repo: [
                {"file": entry.filename, "count": entry.count}
                for entry in report.entries
            ]
            for repo, report in per.items()
        },
        "combined": [
            {"file": entry.filename, "count": entry.count}
            for entry in combined.entries
        ],
        "total_files_touched": combined.total_files,
    }


def format_all_churn_reports(
    commits_by_repo: Dict[str, List[GitCommit]],
    top_n: int = 10,
) -> str:
    """Format a human-readable churn section for all repositories.

    Args:
        commits_by_repo: Mapping of repo name to its list of commits.
        top_n: Maximum number of files to list per repo.

    Returns:
        Multi-line string suitable for inclusion in a digest report.
    """
    per = churn_per_repo(commits_by_repo)
    lines: List[str] = ["## File Churn\n"]

    for repo, report in per.items():
        lines.append(f"### {repo}")
        if report.total_files == 0:
            lines.append("  (no file changes recorded)")
        else:
            for entry in report.top(top_n):
                lines.append(f"  {entry.filename}: {entry.count} change(s)")
        lines.append("")

    combined = combined_churn(commits_by_repo)
    if len(commits_by_repo) > 1 and combined.total_files > 0:
        lines.append("### Combined (all repos)")
        for entry in combined.top(top_n):
            lines.append(f"  {entry.filename}: {entry.count} change(s)")
        lines.append("")

    return "\n".join(lines)
