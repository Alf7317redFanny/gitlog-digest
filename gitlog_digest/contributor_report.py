"""Generates a contributor report dict suitable for JSON export or display."""

from typing import Any, Dict, List

from gitlog_digest.contributor_summary import ContributorSummary


def contributor_report_dict(summary: ContributorSummary) -> Dict[str, Any]:
    """Serialise a ContributorSummary to a plain dict."""
    top = summary.top_contributor()
    return {
        "total_contributors": summary.total_contributors,
        "most_active": top.author if top else None,
        "contributors": [
            {
                "author": entry.author,
                "commit_count": entry.commit_count,
                "repos": entry.repos,
                "subjects": entry.subjects,
            }
            for entry in summary.sorted_entries()
        ],
    }


def format_contributor_report_text(summary: ContributorSummary) -> str:
    """Produce a plain-text contributor report with aligned columns."""
    if not summary.entries:
        return "No contributor data available."

    lines = ["Contributor Report", "=================="]
    for entry in summary.sorted_entries():
        repos_str = ", ".join(entry.repos)
        lines.append(
            f"  {entry.author:<30} {entry.commit_count:>4} commit(s)  repos: {repos_str}"
        )
    lines.append("")
    top = summary.top_contributor()
    if top:
        lines.append(f"Top contributor: {top.author} with {top.commit_count} commit(s)")
    lines.append(f"Unique contributors: {summary.total_contributors}")
    return "\n".join(lines)
