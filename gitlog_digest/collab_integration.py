"""Integration helpers for co-authorship reports across multiple repos."""
from __future__ import annotations

from typing import Dict, List

from gitlog_digest.commit_collab import (
    CommitCollabReport,
    build_collab_report,
    format_collab_report,
)
from gitlog_digest.git_reader import GitCommit


def collab_per_repo(
    commits_by_repo: Dict[str, List[GitCommit]],
) -> Dict[str, CommitCollabReport]:
    """Return a CollabReport for each repository."""
    return {repo: build_collab_report(commits) for repo, commits in commits_by_repo.items()}


def combined_collab(commits_by_repo: Dict[str, List[GitCommit]]) -> CommitCollabReport:
    """Merge all commits into a single cross-repo CollabReport."""
    all_commits: List[GitCommit] = []
    for commits in commits_by_repo.values():
        all_commits.extend(commits)
    return build_collab_report(all_commits)


def collab_report_dict(
    commits_by_repo: Dict[str, List[GitCommit]], n: int = 5
) -> dict:
    per_repo = collab_per_repo(commits_by_repo)
    combined = combined_collab(commits_by_repo)
    return {
        "repos": {
            repo: [{"author_a": p.author_a, "author_b": p.author_b, "shared_files": p.shared_files}
                   for p in report.top(n)]
            for repo, report in per_repo.items()
        },
        "combined": [
            {"author_a": p.author_a, "author_b": p.author_b, "shared_files": p.shared_files}
            for p in combined.top(n)
        ],
    }


def format_all_collab_reports(
    commits_by_repo: Dict[str, List[GitCommit]], n: int = 5
) -> str:
    sections: List[str] = []
    for repo, commits in commits_by_repo.items():
        report = build_collab_report(commits)
        sections.append(f"[{repo}]\n{format_collab_report(report, n)}")
    combined = combined_collab(commits_by_repo)
    sections.append(f"[combined]\n{format_collab_report(combined, n)}")
    return "\n\n".join(sections)
