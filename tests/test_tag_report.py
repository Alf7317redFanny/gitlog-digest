"""Tests for gitlog_digest.tag_report."""

from datetime import datetime

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.tag_report import build_tag_report, tag_stats_dict


def _c(subject: str, sha: str = "deadbeef") -> GitCommit:
    return GitCommit(
        sha=sha,
        author="Bob",
        date=datetime(2024, 6, 10, 9, 0, 0),
        subject=subject,
    )


def test_build_tag_report_contains_section_header():
    commits = [_c("feat: add login", "aaa0001")]
    report = build_tag_report(commits)
    assert "### Features" in report


def test_build_tag_report_contains_sha():
    commits = [_c("fix: null pointer", "abc1234")]
    report = build_tag_report(commits)
    assert "abc1234" in report


def test_build_tag_report_scope_shown():
    commits = [_c("fix(auth): token refresh", "bbb0001")]
    report = build_tag_report(commits)
    assert "(auth)" in report


def test_build_tag_report_breaking_label():
    commits = [_c("feat!: new api", "ccc0001")]
    report = build_tag_report(commits)
    assert "[BREAKING]" in report
    assert "breaking change" in report


def test_build_tag_report_empty():
    report = build_tag_report([])
    assert report == "No commits to summarise."


def test_build_tag_report_ordering():
    commits = [
        _c("chore: clean up", "d01"),
        _c("feat: new thing", "d02"),
        _c("fix: bug", "d03"),
    ]
    report = build_tag_report(commits)
    feat_pos = report.index("### Features")
    fix_pos = report.index("### Bug Fixes")
    chore_pos = report.index("### Chores")
    assert feat_pos < fix_pos < chore_pos


def test_tag_stats_dict_structure():
    commits = [
        _c("feat: a", "e01"),
        _c("feat: b", "e02"),
        _c("fix!: c", "e03"),
    ]
    stats = tag_stats_dict(commits)
    assert stats["by_type"]["feat"] == 2
    assert stats["by_type"]["fix"] == 1
    assert stats["breaking_changes"] == 1
    assert stats["total"] == 3


def test_tag_stats_dict_empty():
    stats = tag_stats_dict([])
    assert stats["total"] == 0
    assert stats["breaking_changes"] == 0
    assert stats["by_type"] == {}
