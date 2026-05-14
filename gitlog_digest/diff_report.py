"""Format a DiffSummary into a human-readable report section."""

from __future__ import annotations

from gitlog_digest.diff_stats import DiffSummary


def format_diff_report(summary: DiffSummary, indent: str = "  ") -> str:
    """Return a multi-line string summarising diff statistics."""
    if not summary.stats:
        return f"{indent}No diff data available."

    lines: list[str] = []
    lines.append(f"{indent}Diff Statistics")
    lines.append(f"{indent}---------------")
    lines.append(
        f"{indent}Total insertions : +{summary.total_insertions}"
    )
    lines.append(
        f"{indent}Total deletions  : -{summary.total_deletions}"
    )
    lines.append(
        f"{indent}Net change       : {_signed(summary.total_insertions - summary.total_deletions)}"
    )

    top = summary.most_changed_commit
    if top:
        lines.append(
            f"{indent}Most active SHA  : {top.sha[:7]}  "
            f"(+{top.insertions} / -{top.deletions})"
        )

    return "\n".join(lines)


def _signed(value: int) -> str:
    return f"+{value}" if value >= 0 else str(value)


def diff_report_dict(summary: DiffSummary) -> dict:
    """Return diff summary as a plain dict (useful for JSON export)."""
    result: dict = {
        "total_insertions": summary.total_insertions,
        "total_deletions": summary.total_deletions,
        "net_change": summary.total_insertions - summary.total_deletions,
        "commits": [
            {
                "sha": s.sha,
                "insertions": s.insertions,
                "deletions": s.deletions,
                "net": s.net,
            }
            for s in summary.stats
        ],
    }
    top = summary.most_changed_commit
    result["most_changed_sha"] = top.sha if top else None
    return result
