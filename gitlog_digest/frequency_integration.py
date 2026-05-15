"""High-level helpers that wire commit_frequency into the digest pipeline."""
from __future__ import annotations

from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_frequency import (
    CommitFrequency,
    build_frequency,
    format_frequency_report,
)


def frequency_per_repo(
    repo_commits: Dict[str, Sequence[GitCommit]]
) -> Dict[str, CommitFrequency]:
    """Return a CommitFrequency for each repo keyed by repo name."""
    return {repo: build_frequency(commits) for repo, commits in repo_commits.items()}


def combined_frequency(repo_commits: Dict[str, Sequence[GitCommit]]) -> CommitFrequency:
    """Merge commits from all repos into a single CommitFrequency."""
    all_commits: List[GitCommit] = []
    for commits in repo_commits.values():
        all_commits.extend(commits)
    return build_frequency(all_commits)


def frequency_report_dict(repo_commits: Dict[str, Sequence[GitCommit]]) -> dict:
    """Return a serialisable dict summarising frequency data per repo and overall."""
    per_repo = frequency_per_repo(repo_commits)
    overall = combined_frequency(repo_commits)

    repos_data = {}
    for repo, freq in per_repo.items():
        repos_data[repo] = {
            "total_commits": freq.total,
            "active_days": freq.days_with_commits(),
            "average_per_active_day": round(freq.average, 2),
            "peak_day": freq.peak.day.isoformat() if freq.peak else None,
            "peak_count": freq.peak.count if freq.peak else 0,
        }

    return {
        "repos": repos_data,
        "overall": {
            "total_commits": overall.total,
            "active_days": overall.days_with_commits(),
            "average_per_active_day": round(overall.average, 2),
            "peak_day": overall.peak.day.isoformat() if overall.peak else None,
            "peak_count": overall.peak.count if overall.peak else 0,
        },
    }


def format_all_frequency_reports(
    repo_commits: Dict[str, Sequence[GitCommit]]
) -> str:
    """Render per-repo and combined frequency reports as a single string."""
    sections: List[str] = []
    for repo, freq in frequency_per_repo(repo_commits).items():
        sections.append(f"=== {repo} ===")
        sections.append(format_frequency_report(freq))
        sections.append("")

    if len(repo_commits) > 1:
        sections.append("=== Combined ===")
        sections.append(format_frequency_report(combined_frequency(repo_commits)))

    return "\n".join(sections)
