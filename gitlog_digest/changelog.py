"""Generate a structured changelog from a Digest, grouping commits by repo and date."""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List

from gitlog_digest.digest import Digest
from gitlog_digest.git_reader import GitCommit


@dataclass
class DayEntry:
    """Commits grouped under a single calendar day."""
    day: date
    commits: List[GitCommit] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.commits)


@dataclass
class RepoChangelog:
    """Ordered daily entries for a single repository."""
    repo_name: str
    days: List[DayEntry] = field(default_factory=list)

    @property
    def total_commits(self) -> int:
        return sum(len(d) for d in self.days)


@dataclass
class Changelog:
    """Top-level changelog built from a Digest."""
    week_label: str
    repos: List[RepoChangelog] = field(default_factory=list)

    @property
    def total_commits(self) -> int:
        return sum(r.total_commits for r in self.repos)


def _group_by_day(commits: List[GitCommit]) -> List[DayEntry]:
    """Return commits grouped by date, oldest first."""
    grouped: Dict[date, List[GitCommit]] = {}
    for commit in commits:
        day = commit.date.date()
        grouped.setdefault(day, []).append(commit)
    return [DayEntry(day=d, commits=grouped[d]) for d in sorted(grouped)]


def build_changelog(digest: Digest) -> Changelog:
    """Convert a Digest into a Changelog with per-repo, per-day grouping."""
    changelog = Changelog(week_label=digest.week.label)
    for summary in digest.repos:
        days = _group_by_day(summary.commits)
        changelog.repos.append(
            RepoChangelog(repo_name=summary.repo_name, days=days)
        )
    return changelog


def format_changelog(changelog: Changelog) -> str:
    """Render a Changelog to a plain-text string."""
    lines: List[str] = []
    lines.append(f"Changelog — {changelog.week_label}")
    lines.append("=" * 40)
    for repo in changelog.repos:
        lines.append(f"\n## {repo.repo_name} ({repo.total_commits} commits)")
        for entry in repo.days:
            lines.append(f"  {entry.day.strftime('%A %d %b')}")
            for commit in entry.commits:
                lines.append(f"    {commit.short_sha}  {commit.subject}")
    lines.append("")
    return "\n".join(lines)
