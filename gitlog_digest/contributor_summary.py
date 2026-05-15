"""Builds a per-contributor summary across one or more repos for a week."""

from dataclasses import dataclass, field
from collections import defaultdict
from typing import Dict, List

from gitlog_digest.git_reader import GitCommit


@dataclass
class ContributorEntry:
    author: str
    repos: List[str] = field(default_factory=list)
    commit_count: int = 0
    subjects: List[str] = field(default_factory=list)

    def add_commit(self, repo: str, commit: GitCommit) -> None:
        self.commit_count += 1
        self.subjects.append(commit.subject)
        if repo not in self.repos:
            self.repos.append(repo)

    @property
    def repo_count(self) -> int:
        return len(self.repos)


@dataclass
class ContributorSummary:
    entries: Dict[str, ContributorEntry] = field(default_factory=dict)

    def add(self, repo: str, commit: GitCommit) -> None:
        author = commit.author
        if author not in self.entries:
            self.entries[author] = ContributorEntry(author=author)
        self.entries[author].add_commit(repo, commit)

    @property
    def total_contributors(self) -> int:
        return len(self.entries)

    def top_contributor(self) -> ContributorEntry | None:
        if not self.entries:
            return None
        return max(self.entries.values(), key=lambda e: e.commit_count)

    def sorted_entries(self) -> List[ContributorEntry]:
        return sorted(self.entries.values(), key=lambda e: e.commit_count, reverse=True)


def build_contributor_summary(
    repo_commits: Dict[str, List[GitCommit]]
) -> ContributorSummary:
    """Build a ContributorSummary from a mapping of repo name -> commits."""
    summary = ContributorSummary()
    for repo, commits in repo_commits.items():
        for commit in commits:
            summary.add(repo, commit)
    return summary


def format_contributor_summary(summary: ContributorSummary) -> str:
    """Return a human-readable contributor summary block."""
    if not summary.entries:
        return "No contributors this week."

    lines = ["## Contributors\n"]
    for entry in summary.sorted_entries():
        repo_list = ", ".join(entry.repos)
        lines.append(
            f"  {entry.author}: {entry.commit_count} commit(s) across [{repo_list}]"
        )
    lines.append(f"\nTotal contributors: {summary.total_contributors}")
    top = summary.top_contributor()
    if top:
        lines.append(f"Most active: {top.author} ({top.commit_count} commits)")
    return "\n".join(lines)
