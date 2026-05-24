"""Integration helpers: compute momentum across repos from pipeline results."""
from __future__ import annotations

from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_momentum import (
    CommitMomentumReport,
    build_momentum_report,
    format_momentum_report,
)


def momentum_per_repo(
    current_by_repo: Dict[str, List[GitCommit]],
    previous_by_repo: Dict[str, List[GitCommit]],
) -> Dict[str, CommitMomentumReport]:
    """Return a momentum report for each repo present in current_by_repo."""
    result: Dict[str, CommitMomentumReport] = {}
    for repo, current in current_by_repo.items():
        previous = previous_by_repo.get(repo, [])
        result[repo] = build_momentum_report(current, previous)
    return result


def combined_momentum(
    current_commits: Sequence[GitCommit],
    previous_commits: Sequence[GitCommit],
) -> CommitMomentumReport:
    """Single momentum report aggregated across all repos."""
    return build_momentum_report(current_commits, previous_commits)


def momentum_report_dict(
    report: CommitMomentumReport,
) -> dict:
    return {
        "overall_trend": report.overall_trend,
        "total_delta": report.total_delta,
        "authors": [
            {
                "author": e.author,
                "current": e.current_count,
                "previous": e.previous_count,
                "delta": e.delta,
                "trend": e.trend,
            }
            for e in report.entries()
        ],
    }


def format_all_momentum_reports(
    reports: Dict[str, CommitMomentumReport],
    top_n: int = 10,
) -> str:
    if not reports:
        return ""
    sections = []
    for repo, report in sorted(reports.items()):
        header = f"=== {repo} ==="
        body = format_momentum_report(report, top_n=top_n)
        sections.append(f"{header}\n{body}")
    return "\n\n".join(sections)
