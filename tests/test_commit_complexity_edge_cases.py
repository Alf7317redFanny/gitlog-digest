"""Edge-case tests for commit complexity scoring."""
from datetime import datetime

from gitlog_digest.commit_complexity import CommitComplexityReport, _label, _score
from gitlog_digest.git_reader import GitCommit


def _c(sha="abc1234", author="Alice", subject="chore: update deps") -> GitCommit:
    return GitCommit(sha=sha, author=author, date=datetime(2024, 3, 1), subject=subject)


def test_boundary_trivial_to_moderate():
    assert _label(9) == "trivial"
    assert _label(10) == "moderate"


def test_boundary_moderate_to_complex():
    assert _label(49) == "moderate"
    assert _label(50) == "complex"


def test_top_n_larger_than_entries_returns_all():
    r = CommitComplexityReport()
    r.add_commit(_c(sha="a"))
    r.add_commit(_c(sha="b"))
    assert len(r.top(100)) == 2


def test_top_zero_returns_empty():
    r = CommitComplexityReport()
    r.add_commit(_c())
    assert r.top(0) == []


def test_by_label_unknown_returns_empty():
    r = CommitComplexityReport()
    r.add_commit(_c())
    assert r.by_label("unknown") == []


def test_entries_returns_copy_does_not_mutate():
    r = CommitComplexityReport()
    r.add_commit(_c())
    entries = r.entries()
    entries.clear()
    assert r.total() == 1


def test_multiple_repos_combined_average():
    from gitlog_digest.complexity_integration import complexity_per_repo, combined_complexity
    data = {
        "repo-a": [_c(sha="a")],
        "repo-b": [_c(sha="b")],
    }
    diff = {
        "repo-a": [{"sha": "a", "insertions": 10, "deletions": 0, "files_changed": 0}],
        "repo-b": [{"sha": "b", "insertions": 30, "deletions": 0, "files_changed": 0}],
    }
    reports = complexity_per_repo(data, diff_data=diff)
    combined = combined_complexity(reports)
    # scores: 10, 30 -> avg 20
    assert combined.average_score() == 20.0


def test_missing_diff_data_defaults_to_zero_score():
    from gitlog_digest.complexity_integration import complexity_per_repo
    data = {"repo-a": [_c(sha="xyz")]}
    reports = complexity_per_repo(data, diff_data={})
    entry = reports["repo-a"].entries()[0]
    assert entry.score == 0
    assert entry.label == "trivial"
