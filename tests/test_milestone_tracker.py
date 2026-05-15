"""Tests for gitlog_digest.milestone_tracker."""

from types import SimpleNamespace
import pytest

from gitlog_digest.milestone_tracker import (
    MilestoneHit,
    MilestoneReport,
    check_milestones,
    format_milestone_report,
    DEFAULT_MILESTONES,
)


def _c(sha: str, author: str = "Alice", subject: str = "fix: something"):
    return SimpleNamespace(sha=sha, author=author, subject=subject)


# ---------------------------------------------------------------------------
# MilestoneReport helpers
# ---------------------------------------------------------------------------

def test_milestone_report_starts_empty():
    r = MilestoneReport()
    assert r.total == 0
    assert r.hits == []


def test_milestone_report_add_and_for_repo():
    r = MilestoneReport()
    hit = MilestoneHit(repo="myrepo", milestone=10, actual_count=12,
                       sha="abc1234", author="Bob", subject="feat: x")
    r.add(hit)
    assert r.total == 1
    assert r.for_repo("myrepo") == [hit]
    assert r.for_repo("other") == []


# ---------------------------------------------------------------------------
# check_milestones
# ---------------------------------------------------------------------------

def test_no_milestone_when_below_threshold():
    commits = [_c(f"sha{i}") for i in range(5)]
    report = check_milestones("repo", commits, baseline=0, thresholds=[10])
    assert report.total == 0


def test_milestone_hit_exactly():
    commits = [_c(f"sha{i}") for i in range(10)]
    report = check_milestones("repo", commits, baseline=0, thresholds=[10])
    assert report.total == 1
    hit = report.hits[0]
    assert hit.milestone == 10
    assert hit.sha == "sha9"  # 10th commit (0-indexed 9)
    assert hit.actual_count == 10


def test_milestone_hit_with_baseline():
    commits = [_c(f"sha{i}") for i in range(5)]
    # baseline=8, new_total=13 → crosses 10
    report = check_milestones("repo", commits, baseline=8, thresholds=[10])
    assert report.total == 1
    hit = report.hits[0]
    assert hit.milestone == 10
    # offset = 10 - 8 = 2 → commits[1]
    assert hit.sha == "sha1"


def test_multiple_milestones_in_one_batch():
    commits = [_c(f"s{i}") for i in range(30)]
    report = check_milestones("repo", commits, baseline=0, thresholds=[10, 25])
    assert report.total == 2
    milestones_hit = {h.milestone for h in report.hits}
    assert milestones_hit == {10, 25}


def test_milestone_already_passed_not_re_reported():
    commits = [_c(f"s{i}") for i in range(5)]
    # baseline already past 10
    report = check_milestones("repo", commits, baseline=15, thresholds=[10])
    assert report.total == 0


def test_default_thresholds_used_when_none_given():
    commits = [_c(f"s{i}") for i in range(10)]
    report = check_milestones("repo", commits, baseline=0)
    assert report.total == 1
    assert report.hits[0].milestone == 10


# ---------------------------------------------------------------------------
# format_milestone_report
# ---------------------------------------------------------------------------

def test_format_empty_report():
    r = MilestoneReport()
    out = format_milestone_report(r)
    assert "No milestones" in out


def test_format_report_contains_repo_and_milestone():
    r = MilestoneReport()
    r.add(MilestoneHit(repo="core", milestone=50, actual_count=52,
                       sha="deadbeef", author="Eve", subject="chore: bump"))
    out = format_milestone_report(r)
    assert "core" in out
    assert "50" in out
    assert "deadbee" in out
    assert "Eve" in out
