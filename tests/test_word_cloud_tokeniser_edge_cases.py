"""Edge-case tests for the word-cloud tokeniser and report helpers."""

from gitlog_digest.word_cloud import _tokenise, build_word_cloud, WordCloudReport
from gitlog_digest.git_reader import GitCommit
from datetime import datetime


def _c(subject: str) -> GitCommit:
    return GitCommit(
        sha="deadbeef",
        subject=subject,
        author="tester",
        date=datetime(2024, 3, 1, 12, 0),
    )


def test_tokenise_handles_punctuation():
    tokens = _tokenise("fix: resolve(auth) issue!")
    assert "fix" in tokens
    assert "resolve" in tokens
    assert "auth" in tokens


def test_tokenise_ignores_numbers_only_tokens():
    tokens = _tokenise("bump version 123")
    assert "123" not in tokens


def test_tokenise_handles_camelcase_as_one_token():
    # CamelCase is treated as a single token (no splitting)
    tokens = _tokenise("refactorAuthModule")
    assert "refactorauthmodule" in tokens


def test_build_word_cloud_len_counts_unique_words():
    report = build_word_cloud([_c("add feature"), _c("add test")])
    # unique words: add, feature, test
    assert len(report) == 3


def test_word_cloud_report_top_empty():
    report = WordCloudReport()
    assert report.top(5) == []


def test_word_cloud_report_total_words_zero_when_empty():
    report = WordCloudReport()
    assert report.total_words == 0


def test_build_word_cloud_single_word_subject():
    report = build_word_cloud([_c("refactoring")])
    assert report.counts["refactoring"] == 1
    assert report.total_words == 1


def test_stop_words_not_counted():
    report = build_word_cloud([_c("fix the bug in the module")])
    assert "the" not in report.counts
    assert "in" not in report.counts
