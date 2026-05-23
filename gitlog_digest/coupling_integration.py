"""Integration helpers for commit coupling across multiple repos."""
from __future__ import annotations

from typing import Iterable

from gitlog_digest.commit_coupling import (
    CommitCouplingReport,
    build_coupling_report,
    format_coupling_report,
)
from gitlog_digest.git_reader import GitCommit


def coupling_per_repo(
    commits_by_repo: dict[str, list[GitCommit]],
) -> dict[str, CommitCouplingReport]:
    """Return a coupling report for each repository."""
    return {
        repo: build_coupling_report(commits)
        for repo, commits in commits_by_repo.items()
    }


def combined_coupling(
    commits_by_repo: dict[str, list[GitCommit]],
) -> CommitCouplingReport:
    """Return a single coupling report merged across all repos."""
    all_commits: list[GitCommit] = []
    for commits in commits_by_repo.values():
        all_commits.extend(commits)
    return build_coupling_report(all_commits)


def coupling_report_dict(
    commits_by_repo: dict[str, list[GitCommit]],
    top_n: int = 10,
) -> dict:
    per_repo = coupling_per_repo(commits_by_repo)
    combined = combined_coupling(commits_by_repo)
    return {
        "per_repo": {
            repo: [{"file_a": p.file_a, "file_b": p.file_b, "count": p.count} for p in r.top(top_n)]
            for repo, r in per_repo.items()
        },
        "combined": [{"file_a": p.file_a, "file_b": p.file_b, "count": p.count} for p in combined.top(top_n)],
        "total_unique_pairs": combined.total_pairs(),
    }


def format_all_coupling_reports(
    commits_by_repo: dict[str, list[GitCommit]],
    top_n: int = 10,
) -> str:
    per_repo = coupling_per_repo(commits_by_repo)
    sections: list[str] = []
    for repo, report in per_repo.items():
        header = f"=== {repo} ==="
        body = format_coupling_report(report, top_n)
        sections.append(f"{header}\n{body}")
    combined = combined_coupling(commits_by_repo)
    sections.append(f"=== Combined ===\n{format_coupling_report(combined, top_n)}")
    return "\n\n".join(sections)
