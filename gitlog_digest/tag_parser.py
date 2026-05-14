"""Parse conventional commit tags/types from commit subjects."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from gitlog_digest.git_reader import GitCommit

# Matches conventional commit prefixes like feat:, fix(scope):, chore!: etc.
_CONVENTIONAL_RE = re.compile(
    r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<desc>.+)$"
)

KNOWN_TYPES = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "docs": "Documentation",
    "style": "Style",
    "refactor": "Refactoring",
    "perf": "Performance",
    "test": "Tests",
    "chore": "Chores",
    "ci": "CI",
    "build": "Build",
    "revert": "Reverts",
}


@dataclass
class TaggedCommit:
    commit: GitCommit
    commit_type: str          # e.g. "feat", "fix", or "other"
    scope: Optional[str]      # e.g. "parser" from feat(parser):
    breaking: bool            # True if commit has "!"
    description: str          # cleaned subject after the prefix

    @property
    def type_label(self) -> str:
        return KNOWN_TYPES.get(self.commit_type, "Other")


def parse_commit(commit: GitCommit) -> TaggedCommit:
    """Attempt to parse a conventional commit subject."""
    m = _CONVENTIONAL_RE.match(commit.subject.strip())
    if m:
        return TaggedCommit(
            commit=commit,
            commit_type=m.group("type").lower(),
            scope=m.group("scope"),
            breaking=m.group("breaking") == "!",
            description=m.group("desc").strip(),
        )
    return TaggedCommit(
        commit=commit,
        commit_type="other",
        scope=None,
        breaking=False,
        description=commit.subject.strip(),
    )


@dataclass
class TagSummary:
    by_type: Dict[str, List[TaggedCommit]] = field(default_factory=dict)
    breaking_changes: List[TaggedCommit] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(len(v) for v in self.by_type.values())


def summarise_tags(commits: List[GitCommit]) -> TagSummary:
    """Group commits by their conventional commit type."""
    summary = TagSummary()
    for commit in commits:
        tc = parse_commit(commit)
        summary.by_type.setdefault(tc.commit_type, []).append(tc)
        if tc.breaking:
            summary.breaking_changes.append(tc)
    return summary
