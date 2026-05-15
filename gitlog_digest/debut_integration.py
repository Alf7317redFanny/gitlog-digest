"""High-level helper that wires git_reader + first_commit together.

Typical usage from the CLI or other pipeline code::

    from gitlog_digest.debut_integration import run_debut_check
    text = run_debut_check(
        repo_paths=["/path/to/repo"],
        week=week_range,
        known_authors=["alice", "bob"],
    )
    print(text)
"""
from typing import List, Optional

from gitlog_digest.git_reader import read_commits, get_repo_name
from gitlog_digest.week_range import WeekRange
from gitlog_digest.first_commit import (
    DebutReport,
    build_debut_report,
    format_debut_report,
)


def collect_commits_for_week(
    repo_paths: List[str],
    week: WeekRange,
) -> dict:
    """Read commits from each repo path filtered to *week*.

    Returns a dict mapping repo-name -> list[GitCommit].
    """
    result = {}
    for path in repo_paths:
        name = get_repo_name(path)
        commits = read_commits(path, since=week.start, until=week.end)
        result[name] = commits
    return result


def run_debut_check(
    repo_paths: List[str],
    week: WeekRange,
    known_authors: Optional[List[str]] = None,
) -> str:
    """Return a formatted debut report for the given week and repos."""
    commits_by_repo = collect_commits_for_week(repo_paths, week)
    report = build_debut_report(commits_by_repo, known_authors=known_authors)
    return format_debut_report(report)


def debut_report_dict(
    repo_paths: List[str],
    week: WeekRange,
    known_authors: Optional[List[str]] = None,
) -> dict:
    """Return a JSON-serialisable dict summarising new contributors."""
    commits_by_repo = collect_commits_for_week(repo_paths, week)
    report: DebutReport = build_debut_report(commits_by_repo, known_authors=known_authors)
    return {
        "week": str(week),
        "new_contributor_count": report.total,
        "new_contributors": [
            {
                "author": d.author,
                "repo": d.repo,
                "date": d.date.strftime("%Y-%m-%d"),
                "sha": d.sha[:7],
                "subject": d.subject,
            }
            for d in report.new_contributors
        ],
    }
