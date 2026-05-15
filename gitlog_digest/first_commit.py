"""Detect and report the first (earliest) commit per author across repos."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from gitlog_digest.git_reader import GitCommit


@dataclass
class AuthorDebut:
    """Records the earliest commit seen for a given author."""
    author: str
    sha: str
    subject: str
    date: datetime
    repo: str

    def __str__(self) -> str:
        return (
            f"{self.author} first appeared in '{self.repo}' on "
            f"{self.date.strftime('%Y-%m-%d')}: {self.subject} ({self.sha[:7]})"
        )


@dataclass
class DebutReport:
    """Aggregated first-commit report across one or more repos."""
    debuts: Dict[str, AuthorDebut] = field(default_factory=dict)

    def add(self, repo: str, commit: GitCommit) -> None:
        """Register a commit; keeps the earliest one per author."""
        author = commit.author
        if author not in self.debuts or commit.date < self.debuts[author].date:
            self.debuts[author] = AuthorDebut(
                author=author,
                sha=commit.sha,
                subject=commit.subject,
                date=commit.date,
                repo=repo,
            )

    @property
    def new_contributors(self) -> List[AuthorDebut]:
        """Return debuts sorted by date ascending."""
        return sorted(self.debuts.values(), key=lambda d: d.date)

    @property
    def total(self) -> int:
        return len(self.debuts)


def build_debut_report(
    commits_by_repo: Dict[str, List[GitCommit]],
    known_authors: Optional[List[str]] = None,
) -> DebutReport:
    """Build a DebutReport from a mapping of repo-name -> commits.

    If *known_authors* is provided, only authors NOT in that list are
    included (i.e. genuinely new contributors this period).
    """
    known = {a.lower() for a in (known_authors or [])}
    report = DebutReport()
    for repo, commits in commits_by_repo.items():
        for commit in commits:
            if known and commit.author.lower() in known:
                continue
            report.add(repo, commit)
    return report


def format_debut_report(report: DebutReport) -> str:
    """Return a human-readable text block for the debut report."""
    if not report.total:
        return "No new contributors this period.\n"
    lines = [f"New contributors ({report.total}):", ""]
    for debut in report.new_contributors:
        lines.append(f"  - {debut}")
    lines.append("")
    return "\n".join(lines)
