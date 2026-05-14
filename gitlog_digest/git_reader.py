"""Module for reading git log data from local repositories."""

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class GitCommit:
    sha: str
    author: str
    email: str
    date: datetime
    message: str
    repo_path: str

    @property
    def short_sha(self) -> str:
        return self.sha[:7]

    @property
    def subject(self) -> str:
        return self.message.splitlines()[0] if self.message else ""


def read_commits(
    repo_path: str,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    branch: str = "HEAD",
) -> list[GitCommit]:
    """Read commits from a git repository within an optional date range."""
    path = Path(repo_path).resolve()
    if not (path / ".git").exists():
        raise ValueError(f"{repo_path!r} is not a git repository")

    fmt = "%H%x1f%an%x1f%ae%x1f%aI%x1f%s"
    cmd = ["git", "-C", str(path), "log", branch, f"--format={fmt}"]

    if since:
        cmd += [f"--since={since.isoformat()}"]
    if until:
        cmd += [f"--until={until.isoformat()}"]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    commits = []
    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f")
        if len(parts) != 5:
            continue
        sha, author, email, date_str, message = parts
        commits.append(
            GitCommit(
                sha=sha,
                author=author,
                email=email,
                date=datetime.fromisoformat(date_str),
                message=message,
                repo_path=str(path),
            )
        )
    return commits


def get_repo_name(repo_path: str) -> str:
    """Return the repository name from its path."""
    path = Path(repo_path).resolve()
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip()).name
