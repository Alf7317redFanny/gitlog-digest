"""Integration helpers for hotspot reports across multiple repos."""
from __future__ import annotations

from typing import Dict, Iterable, List

from gitlog_digest.commit_hotspot import (
    CommitHotspotReport,
    HotspotEntry,
    build_hotspot_report,
    format_hotspot_report,
)
from gitlog_digest.git_reader import GitCommit


def hotspots_per_repo(
    repo_commits: Dict[str, List[GitCommit]],
) -> Dict[str, CommitHotspotReport]:
    """Return a hotspot report keyed by repo name."""
    return {repo: build_hotspot_report(commits) for repo, commits in repo_commits.items()}


def combined_hotspot(
    repo_commits: Dict[str, List[GitCommit]],
) -> CommitHotspotReport:
    """Merge all commits across repos into one hotspot report."""
    all_commits: List[GitCommit] = [
        c for commits in repo_commits.values() for c in commits
    ]
    return build_hotspot_report(all_commits)


def hotspot_report_dict(
    report: CommitHotspotReport, top_n: int = 10
) -> dict:
    entries = report.top(top_n)
    peak = report.peak()
    return {
        "total_files": report.total_files(),
        "peak_file": str(peak) if peak else None,
        "hotspots": [{"path": e.path, "count": e.count} for e in entries],
    }


def format_all_hotspot_reports(
    repo_commits: Dict[str, List[GitCommit]], top_n: int = 10
) -> str:
    per_repo = hotspots_per_repo(repo_commits)
    sections: List[str] = []
    for repo, report in per_repo.items():
        header = f"=== {repo} ==="
        body = format_hotspot_report(report, top_n=top_n)
        sections.append(f"{header}\n{body}")
    combined = combined_hotspot(repo_commits)
    sections.append("=== Combined ===\n" + format_hotspot_report(combined, top_n=top_n))
    return "\n\n".join(sections)
