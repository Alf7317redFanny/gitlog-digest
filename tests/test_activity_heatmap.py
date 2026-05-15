"""Tests for gitlog_digest.activity_heatmap."""

from datetime import datetime

import pytest

from gitlog_digest.activity_heatmap import (
    ActivityHeatmap,
    build_heatmap,
    format_heatmap,
    DAYS,
)
from gitlog_digest.git_reader import GitCommit


def _c(date: datetime) -> GitCommit:
    return GitCommit(sha="abc1234", author="Alice", date=date, message="chore: test")


# Fixed reference dates (week of 2024-01-15)
MON = datetime(2024, 1, 15)  # weekday 0
WED = datetime(2024, 1, 17)  # weekday 2
FRI = datetime(2024, 1, 19)  # weekday 4
SAT = datetime(2024, 1, 20)  # weekday 5


def test_empty_commits_all_zeros():
    heatmap = build_heatmap([])
    assert heatmap.total == 0
    assert all(v == 0 for v in heatmap.counts.values())


def test_single_commit_counted_on_correct_day():
    heatmap = build_heatmap([_c(WED)])
    assert heatmap.counts[2] == 1
    assert heatmap.total == 1


def test_multiple_commits_same_day():
    commits = [_c(MON), _c(MON), _c(MON)]
    heatmap = build_heatmap(commits)
    assert heatmap.counts[0] == 3


def test_commits_spread_across_days():
    commits = [_c(MON), _c(WED), _c(FRI), _c(FRI)]
    heatmap = build_heatmap(commits)
    assert heatmap.counts[0] == 1
    assert heatmap.counts[2] == 1
    assert heatmap.counts[4] == 2
    assert heatmap.total == 4


def test_peak_day_returns_correct_name():
    commits = [_c(FRI), _c(FRI), _c(MON)]
    heatmap = build_heatmap(commits)
    assert heatmap.peak_day == "Fri"


def test_peak_day_no_commits():
    heatmap = ActivityHeatmap()
    assert heatmap.peak_day == "N/A"


def test_format_heatmap_empty():
    heatmap = build_heatmap([])
    output = format_heatmap(heatmap)
    assert "no commits" in output


def test_format_heatmap_contains_all_days():
    commits = [_c(MON), _c(WED), _c(SAT)]
    heatmap = build_heatmap(commits)
    output = format_heatmap(heatmap)
    for day in DAYS:
        assert day in output


def test_format_heatmap_shows_peak_day():
    commits = [_c(WED), _c(WED), _c(MON)]
    heatmap = build_heatmap(commits)
    output = format_heatmap(heatmap)
    assert "Wed" in output
    assert "Peak day" in output
