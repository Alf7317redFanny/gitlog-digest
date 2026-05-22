"""Integration helpers: build recency reports per repo and combined."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_recency import (
    CommitRecencyReport,
    build_recency_report,
    format_recency_report,
    recency_report_dict,
)


def recency_per_repo(
    repo_commits: Dict[str, Sequence[GitCommit]],
    now: datetime | None = None,
) -> Dict[str, CommitRecencyReport]:
    """Return a recency report for each repo."""
    return {
        repo: build_recency_report(commits, now=now)
        for repo, commits in repo_commits.items()
    }


def combined_recency(
    repo_commits: Dict[str, Sequence[GitCommit]],
    now: datetime | None = None,
) -> CommitRecencyReport:
    """Merge all commits across repos into one recency report."""
    all_commits: List[GitCommit] = [
        c for commits in repo_commits.values() for c in commits
    ]
    return build_recency_report(all_commits, now=now)


def all_recency_report_dicts(
    repo_commits: Dict[str, Sequence[GitCommit]],
    now: datetime | None = None,
) -> Dict[str, dict]:
    """Return serialisable dicts for each repo plus a combined entry."""
    per_repo = recency_per_repo(repo_commits, now=now)
    result = {repo: recency_report_dict(r) for repo, r in per_repo.items()}
    result["__combined__"] = recency_report_dict(combined_recency(repo_commits, now=now))
    return result


def format_all_recency_reports(
    repo_commits: Dict[str, Sequence[GitCommit]],
    now: datetime | None = None,
) -> str:
    """Format recency reports for all repos as a single text block."""
    per_repo = recency_per_repo(repo_commits, now=now)
    sections = []
    for repo, report in per_repo.items():
        sections.append(f"[{repo}]")
        sections.append(format_recency_report(report))
    combined = combined_recency(repo_commits, now=now)
    sections.append("[combined]")
    sections.append(format_recency_report(combined))
    return "\n".join(sections)
