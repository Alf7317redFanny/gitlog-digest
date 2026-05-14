"""Build a digest summary from commits grouped by repository."""

from collections import defaultdict
from dataclasses import dataclass, field

from .git_reader import GitCommit, get_repo_name, read_commits
from .week_range import WeekRange


@dataclass
class RepoSummary:
    name: str
    path: str
    commits: list[GitCommit] = field(default_factory=list)

    @property
    def commit_count(self) -> int:
        return len(self.commits)

    @property
    def authors(self) -> list[str]:
        return sorted({c.author for c in self.commits})


@dataclass
class Digest:
    week: WeekRange
    repos: list[RepoSummary] = field(default_factory=list)

    @property
    def total_commits(self) -> int:
        return sum(r.commit_count for r in self.repos)

    @property
    def active_repos(self) -> list[RepoSummary]:
        return [r for r in self.repos if r.commit_count > 0]


def build_digest(repo_paths: list[str], week: WeekRange) -> Digest:
    """Collect commits from all repos for the given week and return a Digest."""
    digest = Digest(week=week)

    for path in repo_paths:
        try:
            name = get_repo_name(path)
            commits = read_commits(path, since=week.start, until=week.end)
            digest.repos.append(RepoSummary(name=name, path=path, commits=commits))
        except Exception as exc:  # noqa: BLE001
            # Skip repos that can't be read but don't crash the whole run
            print(f"[warn] skipping {path!r}: {exc}")

    return digest


def author_breakdown(digest: Digest) -> dict[str, int]:
    """Return a mapping of author name -> total commit count across all repos."""
    counts: dict[str, int] = defaultdict(int)
    for repo in digest.repos:
        for commit in repo.commits:
            counts[commit.author] += 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))
