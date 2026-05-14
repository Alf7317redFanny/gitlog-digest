"""Renders digest output using simple text templates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from gitlog_digest.digest import Digest
from gitlog_digest.stats import CommitStats


_DEFAULT_TEMPLATE = """\
# Git Activity Digest — {week_label}

{repo_sections}
---
Total commits across all repos: {total_commits}
"""

_REPO_SECTION_TEMPLATE = """\
## {repo_name}
- Commits : {commit_count}
- Authors : {authors}
- Top author: {top_author}
- Most active day: {most_active_day}
"""


@dataclass
class TemplateConfig:
    header_template: str = _DEFAULT_TEMPLATE
    repo_template: str = _REPO_SECTION_TEMPLATE
    no_activity_message: str = "_No commits this week._"


def _render_repo_section(repo_name: str, stats: CommitStats, cfg: TemplateConfig) -> str:
    if stats.total == 0:
        return f"## {repo_name}\n{cfg.no_activity_message}\n"

    top = stats.top_author or "—"
    mad = stats.most_active_day or "—"
    authors_str = ", ".join(sorted(stats.unique_authors)) if stats.unique_authors else "—"

    return cfg.repo_template.format(
        repo_name=repo_name,
        commit_count=stats.total,
        authors=authors_str,
        top_author=top,
        most_active_day=mad,
    )


def render_digest(
    digest: Digest,
    stats_map: dict[str, CommitStats],
    cfg: Optional[TemplateConfig] = None,
) -> str:
    """Render a full digest to a string using the given template config."""
    if cfg is None:
        cfg = TemplateConfig()

    repo_sections = ""
    for repo_name, summary in digest.repos.items():
        repo_stats = stats_map.get(repo_name)
        if repo_stats is None:
            repo_sections += f"## {repo_name}\n{cfg.no_activity_message}\n"
        else:
            repo_sections += _render_repo_section(repo_name, repo_stats, cfg)

    return cfg.header_template.format(
        week_label=digest.week.label(),
        repo_sections=repo_sections.strip(),
        total_commits=digest.total_commits(),
    )
