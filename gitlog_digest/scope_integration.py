"""Integration helpers that build scope reports across multiple repos."""

from __future__ import annotations

from typing import Dict, Iterable, List

from gitlog_digest.commit_scope import (
    CommitScopeReport,
    build_scope_report,
    format_scope_report,
    scope_report_dict,
)
from gitlog_digest.git_reader import GitCommit


def scopes_per_repo(
    repo_commits: Dict[str, List[GitCommit]],
) -> Dict[str, CommitScopeReport]:
    """Return a scope report keyed by repo name."""
    return {repo: build_scope_report(commits) for repo, commits in repo_commits.items()}


def combined_scope(reports: Iterable[CommitScopeReport]) -> CommitScopeReport:
    """Merge multiple scope reports into one aggregate report."""
    merged = CommitScopeReport()
    for report in reports:
        for entry in report.scopes():
            # Reconstruct synthetic commits isn't possible — merge counts directly.
            if entry.scope not in merged._scopes:
                from gitlog_digest.commit_scope import ScopeEntry
                merged._scopes[entry.scope] = ScopeEntry(scope=entry.scope)
            merged._scopes[entry.scope].file_count += entry.file_count
            merged._scopes[entry.scope].commit_count += entry.commit_count
    return merged


def all_scope_report_dicts(
    repo_commits: Dict[str, List[GitCommit]],
) -> Dict[str, dict]:
    """Return a dict of scope_report_dict per repo."""
    per_repo = scopes_per_repo(repo_commits)
    return {repo: scope_report_dict(r) for repo, r in per_repo.items()}


def format_all_scope_reports(
    repo_commits: Dict[str, List[GitCommit]],
    top_n: int = 5,
) -> str:
    """Format scope reports for all repos as a single string."""
    per_repo = scopes_per_repo(repo_commits)
    sections: List[str] = []
    for repo, report in per_repo.items():
        sections.append(f"### {repo}")
        sections.append(format_scope_report(report, top_n=top_n))
    if repo_commits:
        merged = combined_scope(per_repo.values())
        sections.append("### Combined")
        sections.append(format_scope_report(merged, top_n=top_n))
    return "\n\n".join(sections)
