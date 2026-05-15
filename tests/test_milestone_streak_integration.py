"""Integration: milestone_tracker + streak used together on shared commit data."""

from datetime import date, datetime
from types import SimpleNamespace

from gitlog_digest.milestone_tracker import check_milestones, format_milestone_report
from gitlog_digest.streak import compute_streaks, format_streak_report


def _c(i: int, author: str = "Dev"):
    d = date(2024, 1, 1 + (i % 28))  # spread across January
    return SimpleNamespace(
        sha=f"sha{i:04d}",
        author=author,
        subject=f"commit number {i}",
        date=datetime(d.year, d.month, d.day),
    )


def test_milestone_and_streak_on_same_commits():
    commits = [_c(i) for i in range(25)]

    # Milestone: crosses 10 and 25
    m_report = check_milestones("myrepo", commits, baseline=0, thresholds=[10, 25])
    assert m_report.total == 2

    # Streak: all 25 commits from one author spread over 25 days
    streaks = compute_streaks(commits)
    assert len(streaks) == 1
    assert streaks[0].author == "Dev"


def test_combined_output_is_non_empty():
    commits = [_c(i) for i in range(10)]
    m_report = check_milestones("repo", commits, baseline=0, thresholds=[10])
    streaks = compute_streaks(commits)

    out = format_milestone_report(m_report) + "\n" + format_streak_report(streaks)
    assert "repo" in out
    assert "Dev" in out
    assert len(out) > 50


def test_multi_author_milestones_and_streaks():
    commits = [_c(i, author="Alice" if i % 2 == 0 else "Bob") for i in range(20)]

    m_report = check_milestones("shared", commits, baseline=0, thresholds=[10, 20])
    assert m_report.total == 2

    streaks = compute_streaks(commits)
    authors = {s.author for s in streaks}
    assert "Alice" in authors
    assert "Bob" in authors
