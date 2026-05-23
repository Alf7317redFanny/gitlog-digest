"""Integration helpers for commit complexity across multiple repos."""
from __future__ import annotations

from typing import Dict, List

from gitlog_digest.commit_complexity import CommitComplexityReport
from gitlog_digest.git_reader import GitCommit


def complexity_per_repo(
    repo_commits: Dict[str, List[GitCommit]],
    diff_data: Dict[str, List[Dict]] | None = None,
) -> Dict[str, CommitComplexityReport]:
    """Build a complexity report for each repo.

    diff_data maps repo_name -> list of dicts with keys:
    sha, insertions, deletions, files_changed.
    """
    diff_data = diff_data or {}
    reports: Dict[str, CommitComplexityReport] = {}
    for repo, commits in repo_commits.items():
        report = CommitComplexityReport()
        diff_index = {d["sha"]: d for d in diff_data.get(repo, [])}
        for commit in commits:
            d = diff_index.get(commit.sha, {})
            report.add_commit(
                commit,
                insertions=d.get("insertions", 0),
                deletions=d.get("deletions", 0),
                files_changed=d.get("files_changed", 0),
            )
        reports[repo] = report
    return reports


def combined_complexity(
    reports: Dict[str, CommitComplexityReport],
) -> CommitComplexityReport:
    """Merge all per-repo reports into one aggregate report."""
    combined = CommitComplexityReport()
    for report in reports.values():
        for entry in report.entries():
            combined._entries.append(entry)
    return combined


def complexity_report_dict(report: CommitComplexityReport) -> dict:
    return {
        "total": report.total(),
        "average_score": round(report.average_score(), 2),
        "trivial": len(report.by_label("trivial")),
        "moderate": len(report.by_label("moderate")),
        "complex": len(report.by_label("complex")),
        "top_complex": [
            {"sha": e.sha[:7], "score": e.score, "subject": e.subject}
            for e in report.top(5)
        ],
    }


def format_all_complexity_reports(
    reports: Dict[str, CommitComplexityReport],
) -> str:
    lines: List[str] = []
    for repo, report in reports.items():
        lines.append(f"## {repo} — Commit Complexity")
        lines.append(
            f"  total={report.total()}  avg_score={report.average_score():.1f}"
        )
        lines.append(
            f"  trivial={len(report.by_label('trivial'))}  "
            f"moderate={len(report.by_label('moderate'))}  "
            f"complex={len(report.by_label('complex'))}"
        )
        if report.top(3):
            lines.append("  Top complex commits:")
            for e in report.top(3):
                lines.append(f"    {e}")
        lines.append("")
    return "\n".join(lines)
