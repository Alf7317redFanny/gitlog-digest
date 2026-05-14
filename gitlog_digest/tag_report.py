"""Build and format a tag-based (conventional commits) report section."""

from __future__ import annotations

from typing import List

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.tag_parser import KNOWN_TYPES, TagSummary, summarise_tags


_ORDER = ["feat", "fix", "perf", "refactor", "docs", "test", "build", "ci", "chore", "revert", "style", "other"]


def _type_label(commit_type: str) -> str:
    return KNOWN_TYPES.get(commit_type, "Other")


def build_tag_report(commits: List[GitCommit]) -> str:
    """Return a formatted string summarising commits by conventional type."""
    summary: TagSummary = summarise_tags(commits)

    if not summary.total:
        return "No commits to summarise."

    lines: List[str] = []

    # Sort types by preferred order, then alphabetically for unknowns
    def sort_key(t: str) -> tuple:
        try:
            return (0, _ORDER.index(t))
        except ValueError:
            return (1, t)

    for ctype in sorted(summary.by_type.keys(), key=sort_key):
        tagged = summary.by_type[ctype]
        label = _type_label(ctype)
        lines.append(f"### {label} ({len(tagged)})")
        for tc in tagged:
            scope_part = f"({tc.scope}) " if tc.scope else ""
            breaking_part = " [BREAKING]" if tc.breaking else ""
            lines.append(f"  - {scope_part}{tc.description}{breaking_part}  [{tc.commit.sha[:7]}]")
        lines.append("")

    if summary.breaking_changes:
        lines.append(f"⚠️  {len(summary.breaking_changes)} breaking change(s) this period.")

    return "\n".join(lines).rstrip()


def tag_stats_dict(commits: List[GitCommit]) -> dict:
    """Return a plain dict of type -> count, suitable for JSON export."""
    summary = summarise_tags(commits)
    return {
        "by_type": {k: len(v) for k, v in summary.by_type.items()},
        "breaking_changes": len(summary.breaking_changes),
        "total": summary.total,
    }
