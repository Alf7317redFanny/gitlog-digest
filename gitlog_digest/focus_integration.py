"""Integration helpers for commit focus reports across multiple repos."""
from __future__ import annotations

from typing import Dict, List

from gitlog_digest.commit_focus import (
    CommitFocusReport,
    FocusEntry,
    build_focus_report,
)
from gitlog_digest.git_reader import GitCommit


def focus_per_repo(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> Dict[str, CommitFocusReport]:
    """Return a focus report keyed by repo name."""
    return {repo: build_focus_report(commits) for repo, commits in commits_by_repo.items()}


def combined_focus(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> CommitFocusReport:
    """Merge focus reports from all repos into one."""
    all_commits: List[GitCommit] = []
    for commits in commits_by_repo.values():
        all_commits.extend(commits)
    return build_focus_report(all_commits)


def focus_report_dict(report: CommitFocusReport, n: int = 10) -> dict:
    """Serialise a focus report to a plain dict."""
    return {
        "total_directories": report.total_directories,
        "top": [
            {
                "directory": e.directory,
                "commit_count": e.commit_count,
                "unique_authors": e.unique_authors,
            }
            for e in report.top(n)
        ],
    }


def format_all_focus_reports(
    commits_by_repo: Dict[str, List[GitCommit]],
    n: int = 10,
) -> str:
    """Return a human-readable focus section covering all repos."""
    lines: List[str] = []
    per_repo = focus_per_repo(commits_by_repo)
    for repo, report in sorted(per_repo.items()):
        lines.append(f"## Focus: {repo}")
        top = report.top(n)
        if not top:
            lines.append("  (no directory-level data)")
        else:
            for entry in top:
                lines.append(f"  {entry}")
        lines.append("")
    combo = combined_focus(commits_by_repo)
    lines.append("## Focus: combined")
    for entry in combo.top(n):
        lines.append(f"  {entry}")
    return "\n".join(lines)
