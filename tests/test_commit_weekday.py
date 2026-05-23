"""Tests for commit_weekday module."""
import pytest
from datetime import datetime, timezone
from gitlog_digest.commit_weekday import (
    build_weekday_report,
    format_weekday_report,
    weekday_report_dict,
    CommitWeekdayReport,
    DAY_NAMES,
)


def _c(day_offset: int, hour: int = 10):
    """Return a minimal commit-like object on a specific weekday.
    day_offset: 0=Monday ... 6=Sunday (using a known Monday as anchor).
    """
    # 2024-01-01 is a Monday
    from datetime import timedelta
    from types import SimpleNamespace
    dt = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc) + timedelta(days=day_offset)
    return SimpleNamespace(date=dt, author="alice", subject="msg")


def test_empty_commits_returns_empty_report():
    report = build_weekday_report([])
    assert report.total == 0
    assert report.peak_day is None
    assert report.weekend_ratio == 0.0


def test_single_commit_counted_on_correct_day():
    report = build_weekday_report([_c(0)])  # Monday
    assert report.total == 1
    assert report.peak_day == "Monday"


def test_multiple_commits_same_day():
    report = build_weekday_report([_c(2), _c(2), _c(2)])  # Wednesday x3
    assert report.total == 3
    assert report.peak_day == "Wednesday"


def test_commits_across_weekdays():
    commits = [_c(0), _c(1), _c(1), _c(4)]  # Mon x1, Tue x2, Fri x1
    report = build_weekday_report(commits)
    assert report.total == 4
    assert report.peak_day == "Tuesday"


def test_weekend_ratio_all_weekend():
    commits = [_c(5), _c(5), _c(6)]  # Saturday x2, Sunday x1
    report = build_weekday_report(commits)
    assert report.weekend_ratio == pytest.approx(1.0)


def test_weekend_ratio_no_weekend():
    commits = [_c(0), _c(1), _c(2)]  # Mon, Tue, Wed
    report = build_weekday_report(commits)
    assert report.weekend_ratio == pytest.approx(0.0)


def test_weekend_ratio_mixed():
    commits = [_c(0), _c(0), _c(5), _c(6)]  # 2 weekday, 2 weekend
    report = build_weekday_report(commits)
    assert report.weekend_ratio == pytest.approx(0.5)


def test_entries_always_returns_seven_days():
    report = build_weekday_report([_c(0)])
    entries = report.entries()
    assert len(entries) == 7
    assert [e.day_name for e in entries] == DAY_NAMES


def test_entries_zero_for_missing_days():
    report = build_weekday_report([_c(3)])  # only Thursday
    entries = report.entries()
    for e in entries:
        if e.day_name == "Thursday":
            assert e.count == 1
        else:
            assert e.count == 0


def test_format_weekday_report_contains_day_names():
    report = build_weekday_report([_c(0), _c(4)])
    text = format_weekday_report(report)
    assert "Monday" in text
    assert "Friday" in text
    assert "Total" in text
    assert "Peak" in text


def test_weekday_report_dict_structure():
    report = build_weekday_report([_c(0), _c(0), _c(6)])
    d = weekday_report_dict(report)
    assert d["total"] == 3
    assert d["peak_day"] == "Monday"
    assert "weekend_ratio" in d
    assert set(d["by_day"].keys()) == set(DAY_NAMES)
    assert d["by_day"]["Monday"] == 2
    assert d["by_day"]["Sunday"] == 1
