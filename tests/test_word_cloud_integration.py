"""Integration tests for word_cloud_integration."""

from datetime import datetime

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.word_cloud_integration import (
    clouds_per_repo,
    combined_cloud,
    format_all_word_cloud_reports,
    word_cloud_report_dict,
)


def _c(subject: str, author: str = "dev") -> GitCommit:
    return GitCommit(
        sha="abc1234",
        subject=subject,
        author=author,
        date=datetime(2024, 1, 15, 9, 0),
    )


REPO_A = [_c("add login feature"), _c("fix login bug"), _c("refactor login module")]
REPO_B = [_c("add signup feature"), _c("improve signup validation")]


def test_clouds_per_repo_keys_match_input():
    result = clouds_per_repo({"repo_a": REPO_A, "repo_b": REPO_B})
    assert set(result.keys()) == {"repo_a", "repo_b"}


def test_clouds_per_repo_independent_counts():
    result = clouds_per_repo({"repo_a": REPO_A, "repo_b": REPO_B})
    assert result["repo_a"].counts["login"] == 3
    assert result["repo_b"].counts["login"] == 0


def test_combined_cloud_merges_all():
    report = combined_cloud({"repo_a": REPO_A, "repo_b": REPO_B})
    assert report.counts["add"] == 2
    assert report.total_words > 0


def test_combined_cloud_empty_input():
    report = combined_cloud({})
    assert len(report) == 0


def test_word_cloud_report_dict_structure():
    d = word_cloud_report_dict({"repo_a": REPO_A})
    assert "per_repo" in d
    assert "combined" in d
    assert "repo_a" in d["per_repo"]
    assert "top_words" in d["combined"]


def test_format_all_contains_repo_names():
    text = format_all_word_cloud_reports({"repo_a": REPO_A, "repo_b": REPO_B})
    assert "repo_a" in text
    assert "repo_b" in text
    assert "Combined" in text


def test_format_all_empty_repos():
    text = format_all_word_cloud_reports({})
    assert "Combined" in text
