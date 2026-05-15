"""Edge-case tests for commit sentiment classification."""

from datetime import datetime

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.commit_sentiment import build_sentiment_report, _classify


def _c(subject: str) -> GitCommit:
    return GitCommit(
        sha="cafebabe",
        short_sha="cafebab",
        subject=subject,
        author="tester",
        date=datetime(2024, 6, 1, 12, 0, 0),
        files_changed=[],
        insertions=0,
        deletions=0,
    )


def test_empty_subject_is_neutral():
    assert _classify("") == "neutral"


def test_subject_with_only_stop_words_is_neutral():
    assert _classify("the a is") == "neutral"


def test_case_insensitive_positive():
    assert _classify("ADD new endpoint") == "positive"


def test_case_insensitive_negative():
    assert _classify("REVERT the change") == "negative"


def test_tie_returns_neutral():
    # one positive, one negative -> tie -> neutral
    assert _classify("fix revert") == "neutral"


def test_all_positive_commits():
    commits = [_c("add feature"), _c("fix bug"), _c("improve performance")]
    report = build_sentiment_report(commits)
    assert len(report.positive) == 3
    assert len(report.negative) == 0
    assert len(report.neutral) == 0
    assert report.positive_ratio == 1.0


def test_all_negative_commits():
    commits = [_c("revert merge"), _c("remove old code"), _c("hack around issue")]
    report = build_sentiment_report(commits)
    assert len(report.negative) == 3
    assert report.negative_ratio == 1.0


def test_ratio_sums_not_exceed_one():
    commits = [_c("add login"), _c("revert deploy"), _c("update readme")]
    report = build_sentiment_report(commits)
    assert report.positive_ratio + report.negative_ratio <= 1.0
