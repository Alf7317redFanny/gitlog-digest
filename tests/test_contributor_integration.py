"""Integration test: contributor summary + report working together."""

from datetime import datetime
from gitlog_digest.git_reader import GitCommit
from gitlog_digest.contributor_summary import build_contributor_summary, format_contributor_summary
from gitlog_digest.contributor_report import contributor_report_dict, format_contributor_report_text


def _c(author: str, subject: str = "chore: update") -> GitCommit:
    return GitCommit(
        sha="cafebabe",
        author=author,
        date=datetime(2024, 6, 5, 12, 0, 0),
        subject=subject,
    )


def test_full_pipeline_multi_repo_multi_author():
    repo_commits = {
        "frontend": [_c("alice"), _c("alice"), _c("bob")],
        "backend": [_c("bob"), _c("carol")],
        "infra": [_c("alice")],
    }
    summary = build_contributor_summary(repo_commits)

    assert summary.total_contributors == 3
    assert summary.entries["alice"].commit_count == 3
    assert summary.entries["bob"].commit_count == 2
    assert summary.entries["carol"].commit_count == 1

    # alice spans frontend + infra
    assert set(summary.entries["alice"].repos) == {"frontend", "infra"}
    # bob spans frontend + backend
    assert set(summary.entries["bob"].repos) == {"frontend", "backend"}

    top = summary.top_contributor()
    assert top.author == "alice"


def test_summary_text_and_report_dict_consistent():
    repo_commits = {"repo": [_c("zara"), _c("zara"), _c("yusuf")]}
    summary = build_contributor_summary(repo_commits)

    text = format_contributor_summary(summary)
    d = contributor_report_dict(summary)
    report_text = format_contributor_report_text(summary)

    assert "zara" in text
    assert d["most_active"] == "zara"
    assert "zara" in report_text
    assert d["total_contributors"] == 2


def test_single_contributor_single_repo():
    repo_commits = {"solo-repo": [_c("eve", "feat: init")]}
    summary = build_contributor_summary(repo_commits)
    d = contributor_report_dict(summary)

    assert d["total_contributors"] == 1
    assert d["most_active"] == "eve"
    assert d["contributors"][0]["subjects"] == ["feat: init"]
