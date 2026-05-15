"""Integration helpers: run sentiment analysis across multiple repos."""

from __future__ import annotations

from typing import Dict, List

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_sentiment import (
    CommitSentimentReport,
    build_sentiment_report,
    format_sentiment_report,
)


def sentiment_per_repo(
    commits_by_repo: Dict[str, List[GitCommit]]
) -> Dict[str, CommitSentimentReport]:
    """Return a sentiment report for each repository."""
    return {
        repo: build_sentiment_report(commits)
        for repo, commits in commits_by_repo.items()
    }


def combined_sentiment(commits_by_repo: Dict[str, List[GitCommit]]) -> CommitSentimentReport:
    """Merge all commits across repos into a single sentiment report."""
    all_commits: List[GitCommit] = []
    for commits in commits_by_repo.values():
        all_commits.extend(commits)
    return build_sentiment_report(all_commits)


def sentiment_report_dict(
    commits_by_repo: Dict[str, List[GitCommit]]
) -> Dict[str, object]:
    """Return a serialisable dict summarising sentiment across all repos."""
    per_repo = sentiment_per_repo(commits_by_repo)
    combined = combined_sentiment(commits_by_repo)
    return {
        "combined": combined.summary_dict(),
        "per_repo": {repo: r.summary_dict() for repo, r in per_repo.items()},
    }


def format_all_sentiment_reports(
    commits_by_repo: Dict[str, List[GitCommit]]
) -> str:
    """Render a human-readable sentiment section for all repos plus a combined total."""
    sections: List[str] = []
    per_repo = sentiment_per_repo(commits_by_repo)
    for repo, report in per_repo.items():
        sections.append(f"### {repo}")
        sections.append(format_sentiment_report(report))
    combined = combined_sentiment(commits_by_repo)
    sections.append("### Combined")
    sections.append(format_sentiment_report(combined))
    return "\n".join(sections)
