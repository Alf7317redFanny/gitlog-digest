"""Integration helpers that wire author ranking into the summary pipeline."""

from __future__ import annotations

from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.author_rank import (
    AuthorRankReport,
    build_author_rank,
    format_author_rank_report,
)


def rank_from_pipeline(
    commits_by_repo: Dict[str, Sequence[GitCommit]],
    top_n: int = 10,
) -> AuthorRankReport:
    """Convenience wrapper used by the summary pipeline."""
    return build_author_rank(commits_by_repo)


def rank_report_dict(
    report: AuthorRankReport,
    top_n: int = 10,
) -> dict:
    """Serialisable dict representation of the rank report."""
    return {
        "total_ranked_authors": len(report),
        "top": [
            {
                "rank": i,
                "author": e.author,
                "commit_count": e.commit_count,
                "repos": sorted(e.repos),
            }
            for i, e in enumerate(report.top(top_n), start=1)
        ],
    }


def format_rank_section(
    commits_by_repo: Dict[str, Sequence[GitCommit]],
    top_n: int = 10,
    heading: str = "Top Contributors",
) -> str:
    """Build and format an author rank section ready for inclusion in a digest."""
    report = build_author_rank(commits_by_repo)
    body = format_author_rank_report(report, top_n=top_n)
    return f"{heading}\n{'=' * len(heading)}\n{body}"
