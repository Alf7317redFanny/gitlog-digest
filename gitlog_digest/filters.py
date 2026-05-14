"""Filtering utilities for git commits."""

from dataclasses import dataclass
from typing import Optional, List
from gitlog_digest.git_reader import GitCommit


@dataclass
class CommitFilter:
    """Criteria for filtering commits."""
    authors: Optional[List[str]] = None
    exclude_authors: Optional[List[str]] = None
    message_contains: Optional[str] = None
    exclude_merges: bool = False


def _normalize(name: str) -> str:
    return name.strip().lower()


def apply_filter(commits: List[GitCommit], f: CommitFilter) -> List[GitCommit]:
    """Return a filtered list of commits based on the given filter criteria."""
    result = commits

    if f.exclude_merges:
        result = [c for c in result if not c.subject.startswith("Merge")]

    if f.authors:
        allowed = {_normalize(a) for a in f.authors}
        result = [c for c in result if _normalize(c.author) in allowed]

    if f.exclude_authors:
        blocked = {_normalize(a) for a in f.exclude_authors}
        result = [c for c in result if _normalize(c.author) not in blocked]

    if f.message_contains:
        needle = f.message_contains.lower()
        result = [c for c in result if needle in c.subject.lower()]

    return result


def filter_by_author(commits: List[GitCommit], author: str) -> List[GitCommit]:
    """Convenience wrapper to filter commits by a single author name."""
    return apply_filter(commits, CommitFilter(authors=[author]))


def exclude_merge_commits(commits: List[GitCommit]) -> List[GitCommit]:
    """Convenience wrapper to strip merge commits."""
    return apply_filter(commits, CommitFilter(exclude_merges=True))
