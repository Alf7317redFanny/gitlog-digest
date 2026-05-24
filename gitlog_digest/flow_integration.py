"""Integration helpers for commit flow reports across multiple repositories."""
from __future__ import annotations

from typing import Dict, List

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_flow import (
    CommitFlowReport,
    FlowEntry,
    build_flow_report,
    format_flow_report,
)


def flow_per_repo(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> Dict[str, CommitFlowReport]:
    """Build a CommitFlowReport for each repository."""
    return {repo: build_flow_report(commits) for repo, commits in commits_by_repo.items()}


def combined_flow(commits_by_repo: Dict[str, List[GitCommit]]) -> CommitFlowReport:
    """Merge all commits across repos into a single CommitFlowReport."""
    all_commits: List[GitCommit] = []
    for commits in commits_by_repo.values():
        all_commits.extend(commits)
    return build_flow_report(all_commits)


def flow_report_dict(commits_by_repo: Dict[str, List[GitCommit]]) -> dict:
    """Return a serialisable dict summarising flow data across all repos."""
    per_repo = flow_per_repo(commits_by_repo)
    combined = combined_flow(commits_by_repo)
    repos_out = {}
    for repo, report in per_repo.items():
        repos_out[repo] = {
            "total": report.total,
            "dominant_type": report.dominant_type(),
            "entries": [
                {
                    "day": str(e.day),
                    "add": e.add,
                    "remove": e.remove,
                    "refactor": e.refactor,
                    "fix": e.fix,
                    "other": e.other,
                }
                for e in report.entries()
            ],
        }
    return {
        "repos": repos_out,
        "combined": {
            "total": combined.total,
            "dominant_type": combined.dominant_type(),
        },
    }


def format_all_flow_reports(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> str:
    """Format flow reports for all repos plus a combined summary."""
    per_repo = flow_per_repo(commits_by_repo)
    sections = [format_flow_report(report, title=repo) for repo, report in per_repo.items()]
    combined = combined_flow(commits_by_repo)
    sections.append(format_flow_report(combined, title="Combined"))
    return "\n\n".join(sections)
