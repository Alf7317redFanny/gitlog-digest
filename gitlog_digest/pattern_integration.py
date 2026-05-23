"""Integration helpers: run pattern analysis across multiple repos."""
from __future__ import annotations

from typing import Dict, List, Optional

from gitlog_digest.commit_pattern import (
    CommitPatternReport,
    PatternEntry,
    build_pattern_report,
)
from gitlog_digest.git_reader import GitCommit


def patterns_per_repo(
    repo_commits: Dict[str, List[GitCommit]]
) -> Dict[str, CommitPatternReport]:
    """Return a pattern report keyed by repo name."""
    return {repo: build_pattern_report(commits) for repo, commits in repo_commits.items()}


def combined_pattern(reports: Dict[str, CommitPatternReport]) -> CommitPatternReport:
    """Merge all per-repo reports into a single aggregate report."""
    from gitlog_digest.commit_pattern import CommitPatternReport, PatternEntry

    merged: CommitPatternReport = CommitPatternReport()
    for report in reports.values():
        for entry in report.sorted_entries():
            if entry.commit_type not in merged._entries:
                merged._entries[entry.commit_type] = PatternEntry(commit_type=entry.commit_type)
            merged._entries[entry.commit_type].dates.extend(entry.dates)
    return merged


def pattern_report_dict(report: CommitPatternReport) -> dict:
    """Serialise a CommitPatternReport to a plain dict."""
    return {
        "total_typed_commits": report.total,
        "top_type": report.top_type,
        "types": [
            {
                "type": e.commit_type,
                "count": e.count,
                "peak_day": e.peak_day.isoformat() if e.peak_day else None,
            }
            for e in report.sorted_entries()
        ],
    }


def format_all_pattern_reports(
    per_repo: Dict[str, CommitPatternReport],
    merged: Optional[CommitPatternReport] = None,
) -> str:
    """Return a human-readable text block for all repos plus an optional combined section."""
    lines: List[str] = []
    for repo, report in per_repo.items():
        lines.append(f"## {repo} — commit patterns")
        if not report.total:
            lines.append("  (no conventional commits)")
        else:
            for e in report.sorted_entries():
                lines.append(f"  {e.commit_type:<12} {e.count:>4} commits")
        lines.append("")
    if merged is not None:
        lines.append("## combined commit patterns")
        for e in merged.sorted_entries():
            lines.append(f"  {e.commit_type:<12} {e.count:>4} commits")
        lines.append("")
    return "\n".join(lines)
