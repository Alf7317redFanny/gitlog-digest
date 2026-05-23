"""Integration helpers for commit language detection across multiple repos."""
from __future__ import annotations

from typing import Dict, Iterable, List

from gitlog_digest.commit_language import (
    CommitLanguageReport,
    LanguageEntry,
    build_language_report,
    merge_reports,
)
from gitlog_digest.git_reader import GitCommit


def reports_per_repo(
    repo_commits: Dict[str, List[GitCommit]],
) -> Dict[str, CommitLanguageReport]:
    """Build a language report for each repository."""
    return {repo: build_language_report(commits) for repo, commits in repo_commits.items()}


def combined_report(
    repo_commits: Dict[str, List[GitCommit]],
) -> CommitLanguageReport:
    """Merge language reports from all repositories into one."""
    individual = reports_per_repo(repo_commits)
    if not individual:
        return CommitLanguageReport()
    return merge_reports(*individual.values())


def language_report_dict(report: CommitLanguageReport, top_n: int = 5) -> dict:
    """Serialise the top languages to a plain dict for JSON export."""
    return {
        "top_languages": [
            {
                "language": e.language,
                "commit_count": e.commit_count,
                "file_count": e.file_count,
            }
            for e in report.top(top_n)
        ],
        "total_languages_detected": len(report),
    }


def format_all_language_reports(
    repo_commits: Dict[str, List[GitCommit]],
    top_n: int = 5,
) -> str:
    """Return a formatted text block showing language breakdown per repo."""
    per_repo = reports_per_repo(repo_commits)
    lines: List[str] = []
    for repo, report in sorted(per_repo.items()):
        lines.append(f"## {repo}")
        top = report.top(top_n)
        if not top:
            lines.append("  (no recognised languages)")
        else:
            for entry in top:
                lines.append(f"  {entry}")
        lines.append("")
    return "\n".join(lines).rstrip()
