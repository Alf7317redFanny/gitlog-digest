"""Integration helpers for commit cadence across multiple repos."""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from gitlog_digest.commit_cadence import (
    CommitCadenceReport,
    CadenceEntry,
    build_cadence_report,
    format_cadence_report,
)
from gitlog_digest.git_reader import GitCommit


def cadence_per_repo(
    repo_commits: Dict[str, Sequence[GitCommit]]
) -> Dict[str, CommitCadenceReport]:
    """Build a cadence report for each repository."""
    return {repo: build_cadence_report(commits) for repo, commits in repo_commits.items()}


def combined_cadence(repo_commits: Dict[str, Sequence[GitCommit]]) -> CommitCadenceReport:
    """Merge commits from all repos into a single cadence report."""
    all_commits: List[GitCommit] = []
    for commits in repo_commits.values():
        all_commits.extend(commits)
    return build_cadence_report(all_commits)


def cadence_report_dict(
    repo_commits: Dict[str, Sequence[GitCommit]]
) -> Dict[str, object]:
    """Return a serialisable dict summarising cadence across all repos."""
    per_repo = cadence_per_repo(repo_commits)
    combined = combined_cadence(repo_commits)

    repos_out = {}
    for repo, report in per_repo.items():
        most_reg: Optional[CadenceEntry] = report.most_regular()
        repos_out[repo] = {
            "total_authors": report.total,
            "most_regular_author": most_reg.author if most_reg else None,
            "most_regular_stdev": most_reg.regularity_score if most_reg else None,
        }

    combined_reg = combined.most_regular()
    return {
        "repos": repos_out,
        "combined": {
            "total_authors": combined.total,
            "most_regular_author": combined_reg.author if combined_reg else None,
            "most_regular_stdev": combined_reg.regularity_score if combined_reg else None,
        },
    }


def format_all_cadence_reports(
    repo_commits: Dict[str, Sequence[GitCommit]], top_n: int = 5
) -> str:
    """Format cadence reports for all repos plus a combined section."""
    sections: List[str] = []
    per_repo = cadence_per_repo(repo_commits)
    for repo, report in per_repo.items():
        sections.append(f"### {repo}")
        sections.append(format_cadence_report(report, top_n=top_n))
    combined = combined_cadence(repo_commits)
    sections.append("### Combined")
    sections.append(format_cadence_report(combined, top_n=top_n))
    return "\n".join(sections)
