"""Wires word-cloud analysis across multiple repos from a pipeline result."""

from __future__ import annotations

from typing import Dict, List

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.word_cloud import (
    WordCloudReport,
    build_word_cloud,
    format_word_cloud_text,
    word_cloud_dict,
)


def clouds_per_repo(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> Dict[str, WordCloudReport]:
    """Build a WordCloudReport for every repo in *commits_by_repo*."""
    return {repo: build_word_cloud(commits) for repo, commits in commits_by_repo.items()}


def combined_cloud(commits_by_repo: Dict[str, List[GitCommit]]) -> WordCloudReport:
    """Merge commits from all repos into a single WordCloudReport."""
    all_commits: List[GitCommit] = []
    for commits in commits_by_repo.values():
        all_commits.extend(commits)
    return build_word_cloud(all_commits)


def word_cloud_report_dict(
    commits_by_repo: Dict[str, List[GitCommit]],
    top_n: int = 10,
) -> Dict:
    """Return a serialisable dict with per-repo and combined word clouds."""
    per_repo = clouds_per_repo(commits_by_repo)
    overall = combined_cloud(commits_by_repo)
    return {
        "per_repo": {repo: word_cloud_dict(report, top_n) for repo, report in per_repo.items()},
        "combined": word_cloud_dict(overall, top_n),
    }


def format_all_word_cloud_reports(
    commits_by_repo: Dict[str, List[GitCommit]],
    top_n: int = 10,
) -> str:
    """Format word-cloud sections for all repos plus a combined section."""
    parts: List[str] = []
    per_repo = clouds_per_repo(commits_by_repo)
    for repo, report in sorted(per_repo.items()):
        parts.append(f"### {repo}")
        parts.append(format_word_cloud_text(report, top_n))
    parts.append("### Combined")
    parts.append(format_word_cloud_text(combined_cloud(commits_by_repo), top_n))
    return "\n".join(parts)
