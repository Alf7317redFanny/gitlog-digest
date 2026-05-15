"""Integration tests for sentiment analysis across multiple repos."""

from datetime import datetime

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.sentiment_integration import (
    sentiment_per_repo,
    combined_sentiment,
    sentiment_report_dict,
    format_all_sentiment_reports,
)


def _c(subject: str, author: str = "dev") -> GitCommit:
    return GitCommit(
        sha="deadbeef",
        short_sha="deadbee",
        subject=subject,
        author=author,
        date=datetime(2024, 3, 4, 9, 0, 0),
        files_changed=[],
        insertions=0,
        deletions=0,
    )


_COMMITS_BY_REPO = {
    "repo-alpha": [_c("add search"), _c("revert deploy"), _c("update ci")],
    "repo-beta": [_c("fix crash"), _c("remove legacy code")],
}


def test_sentiment_per_repo_keys_match_input():
    result = sentiment_per_repo(_COMMITS_BY_REPO)
    assert set(result.keys()) == {"repo-alpha", "repo-beta"}


def test_sentiment_per_repo_totals():
    result = sentiment_per_repo(_COMMITS_BY_REPO)
    assert result["repo-alpha"].total == 3
    assert result["repo-beta"].total == 2


def test_combined_sentiment_total():
    report = combined_sentiment(_COMMITS_BY_REPO)
    assert report.total == 5


def test_combined_sentiment_counts_correctly():
    report = combined_sentiment(_COMMITS_BY_REPO)
    d = report.summary_dict()
    assert d["positive"] + d["negative"] + d["neutral"] == 5


def test_sentiment_report_dict_structure():
    d = sentiment_report_dict(_COMMITS_BY_REPO)
    assert "combined" in d
    assert "per_repo" in d
    assert "repo-alpha" in d["per_repo"]
    assert "repo-beta" in d["per_repo"]


def test_sentiment_report_dict_combined_matches_combined():
    d = sentiment_report_dict(_COMMITS_BY_REPO)
    combined = combined_sentiment(_COMMITS_BY_REPO)
    assert d["combined"] == combined.summary_dict()


def test_format_all_reports_contains_repo_names():
    text = format_all_sentiment_reports(_COMMITS_BY_REPO)
    assert "repo-alpha" in text
    assert "repo-beta" in text


def test_format_all_reports_contains_combined():
    text = format_all_sentiment_reports(_COMMITS_BY_REPO)
    assert "Combined" in text


def test_empty_repos_returns_combined_section():
    text = format_all_sentiment_reports({})
    assert "Combined" in text
