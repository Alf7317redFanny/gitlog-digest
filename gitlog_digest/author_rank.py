"""Rank authors by commit volume across one or more repositories."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit


@dataclass
class AuthorRankEntry:
    author: str
    commit_count: int
    repos: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        repo_str = ", ".join(sorted(self.repos))
        return f"{self.author}: {self.commit_count} commit(s) [{repo_str}]"


@dataclass
class AuthorRankReport:
    entries: List[AuthorRankEntry] = field(default_factory=list)

    def top(self, n: int = 5) -> List[AuthorRankEntry]:
        return self.entries[:n]

    def __len__(self) -> int:
        return len(self.entries)


def build_author_rank(
    commits_by_repo: Dict[str, Sequence[GitCommit]]
) -> AuthorRankReport:
    """Build a ranked list of authors sorted by total commit count descending."""
    counts: Dict[str, int] = {}
    repos_by_author: Dict[str, List[str]] = {}

    for repo, commits in commits_by_repo.items():
        for commit in commits:
            author = commit.author
            counts[author] = counts.get(author, 0) + 1
            if author not in repos_by_author:
                repos_by_author[author] = []
            if repo not in repos_by_author[author]:
                repos_by_author[author].append(repo)

    entries = [
        AuthorRankEntry(
            author=author,
            commit_count=count,
            repos=repos_by_author[author],
        )
        for author, count in sorted(counts.items(), key=lambda x: -x[1])
    ]
    return AuthorRankReport(entries=entries)


def format_author_rank_report(report: AuthorRankReport, top_n: int = 10) -> str:
    """Return a human-readable string for the top N authors."""
    if not report.entries:
        return "No author data available."

    lines = ["Author Rankings", "---------------"]
    for i, entry in enumerate(report.top(top_n), start=1):
        lines.append(f"{i:>2}. {entry}")
    return "\n".join(lines)
