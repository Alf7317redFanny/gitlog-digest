"""Tests for contributor_report module."""

from datetime import datetime
from gitlog_digest.git_reader import GitCommit
from gitlog_digest.contributor_summary import build_contributor_summary
from gitlog_digest.contributor_report import (
    contributor_report_dict,
    format_contributor_report_text,
)


def _c(author: str, subject: str = "fix: something") -> GitCommit:
    return GitCommit(
        sha="deadbeef",
        author=author,
        date=datetime(2024, 6, 4, 9, 0, 0),
        subject=subject,
    )


def _summary(repo_commits):
    return build_contributor_summary(repo_commits)


def test_report_dict_total_contributors():
    s = _summary({"repo-x": [_c("alice"), _c("bob")]})
    d = contributor_report_dict(s)
    assert d["total_contributors"] == 2


def test_report_dict_most_active():
    s = _summary({"repo-x": [_c("alice"), _c("alice"), _c("bob")]})
    d = contributor_report_dict(s)
    assert d["most_active"] == "alice"


def test_report_dict_contributors_list_sorted():
    s = _summary({"repo-x": [_c("bob"), _c("alice"), _c("alice")]})
    d = contributor_report_dict(s)
    assert d["contributors"][0]["author"] == "alice"
    assert d["contributors"][1]["author"] == "bob"


def test_report_dict_includes_repos():
    s = _summary({"my-repo": [_c("alice")]})
    d = contributor_report_dict(s)
    assert "my-repo" in d["contributors"][0]["repos"]


def test_report_dict_includes_subjects():
    s = _summary({"repo": [_c("alice", subject="feat: new thing")]})
    d = contributor_report_dict(s)
    assert "feat: new thing" in d["contributors"][0]["subjects"]


def test_report_dict_empty_summary():
    s = _summary({})
    d = contributor_report_dict(s)
    assert d["total_contributors"] == 0
    assert d["most_active"] is None
    assert d["contributors"] == []


def test_format_text_contains_author():
    s = _summary({"repo": [_c("charlie")]})
    text = format_contributor_report_text(s)
    assert "charlie" in text


def test_format_text_empty():
    from gitlog_digest.contributor_summary import ContributorSummary
    text = format_contributor_report_text(ContributorSummary())
    assert "No contributor data" in text


def test_format_text_shows_commit_count():
    s = _summary({"repo": [_c("dave"), _c("dave"), _c("dave")]})
    text = format_contributor_report_text(s)
    assert "3" in text
    assert "dave" in text
