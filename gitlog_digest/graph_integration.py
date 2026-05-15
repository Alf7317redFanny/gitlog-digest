"""Integration helpers: build and format commit graphs across multiple repos."""
from __future__ import annotations

from typing import Dict, List, Sequence

from gitlog_digest.commit_graph import (
    CommitGraph,
    build_commit_graph,
    format_commit_graph,
)
from gitlog_digest.git_reader import GitCommit


def graphs_per_repo(
    repo_commits: Dict[str, Sequence[GitCommit]]
) -> Dict[str, CommitGraph]:
    """Return a CommitGraph for each repository."""
    return {repo: build_commit_graph(commits) for repo, commits in repo_commits.items()}


def combined_graph(repo_commits: Dict[str, Sequence[GitCommit]]) -> CommitGraph:
    """Merge commits from all repos into a single CommitGraph."""
    all_commits: List[GitCommit] = []
    for commits in repo_commits.values():
        all_commits.extend(commits)
    return build_commit_graph(all_commits)


def graph_report_dict(
    repo_commits: Dict[str, Sequence[GitCommit]]
) -> dict:
    """Return a serialisable dict summarising graphs for all repos plus combined."""
    per_repo = graphs_per_repo(repo_commits)
    combined = combined_graph(repo_commits)
    return {
        "repos": {
            repo: {
                "total": g.total,
                "peak_day": g.peak_day.isoformat() if g.peak_day else None,
                "rows": [
                    {"day": r.day.isoformat(), "count": r.count}
                    for r in g.rows
                ],
            }
            for repo, g in per_repo.items()
        },
        "combined": {
            "total": combined.total,
            "peak_day": combined.peak_day.isoformat() if combined.peak_day else None,
        },
    }


def format_all_graph_reports(
    repo_commits: Dict[str, Sequence[GitCommit]]
) -> str:
    """Render ASCII graphs for every repo followed by a combined graph."""
    parts: List[str] = []
    for repo, commits in repo_commits.items():
        graph = build_commit_graph(commits)
        parts.append(format_commit_graph(graph, title=f"{repo} — Commit Activity"))
    if len(repo_commits) > 1:
        combined = combined_graph(repo_commits)
        parts.append(format_commit_graph(combined, title="Combined — Commit Activity"))
    return "\n".join(parts)
