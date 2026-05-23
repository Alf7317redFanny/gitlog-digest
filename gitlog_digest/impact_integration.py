"""Integration helpers for commit impact across multiple repos."""
from __future__ import annotations

from typing import Dict, List

from gitlog_digest.commit_impact import CommitImpactReport
from gitlog_digest.git_reader import GitCommit


def impact_per_repo(
    commits_by_repo: Dict[str, List[GitCommit]],
    diff_data: Dict[str, List[tuple]],
) -> Dict[str, CommitImpactReport]:
    """Build an impact report per repo.

    diff_data maps repo_name -> list of (files_changed, insertions, deletions)
    aligned with commits_by_repo order.
    """
    reports: Dict[str, CommitImpactReport] = {}
    for repo, commits in commits_by_repo.items():
        report = CommitImpactReport()
        diffs = diff_data.get(repo, [])
        for i, commit in enumerate(commits):
            if i < len(diffs):
                f, ins, dels = diffs[i]
            else:
                f, ins, dels = 0, 0, 0
            report.add_commit(commit, files_changed=f, insertions=ins, deletions=dels)
        reports[repo] = report
    return reports


def combined_impact(
    commits_by_repo: Dict[str, List[GitCommit]],
    diff_data: Dict[str, List[tuple]],
) -> CommitImpactReport:
    """Merge all repos into a single impact report."""
    report = CommitImpactReport()
    for repo, commits in commits_by_repo.items():
        diffs = diff_data.get(repo, [])
        for i, commit in enumerate(commits):
            if i < len(diffs):
                f, ins, dels = diffs[i]
            else:
                f, ins, dels = 0, 0, 0
            report.add_commit(commit, files_changed=f, insertions=ins, deletions=dels)
    return report


def impact_report_dict(report: CommitImpactReport) -> dict:
    peak = report.peak()
    return {
        "total": report.total(),
        "average_score": round(report.average_score(), 2),
        "by_label": report.by_label(),
        "peak": {
            "sha": peak.sha[:7],
            "subject": peak.subject,
            "score": peak.score,
            "label": peak.label,
        } if peak else None,
        "top": [
            {"sha": e.sha[:7], "subject": e.subject, "score": e.score, "label": e.label}
            for e in report.top()
        ],
    }


def format_all_impact_reports(
    reports: Dict[str, CommitImpactReport],
) -> str:
    lines: List[str] = []
    for repo, report in reports.items():
        lines.append(f"## {repo} — Commit Impact")
        if report.total() == 0:
            lines.append("  (no commits)")
        else:
            lines.append(f"  Total: {report.total()}  Avg score: {report.average_score():.1f}")
            for entry in report.top(3):
                lines.append(f"  {entry}")
        lines.append("")
    return "\n".join(lines)
