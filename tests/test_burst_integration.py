"""Tests for burst_integration.py"""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from gitlog_digest.burst_integration import (
    burst_report_dict,
    bursts_per_repo,
    combined_burst,
    format_all_burst_reports,
)


def _c(day: str, hour: int = 10):
    dt = datetime.fromisoformat(f"{day}T{hour:02d}:00:00").replace(
        tzinfo=timezone.utc
    )
    return SimpleNamespace(date=dt, sha="abc", author="dev", subject="x", files=[])


_REPO_A = (
    [_c("2024-01-01")] * 1
    + [_c("2024-01-02")] * 1
    + [_c("2024-01-03")] * 8
)
_REPO_B = [_c("2024-01-01")] * 3 + [_c("2024-01-02")] * 3


def test_bursts_per_repo_keys_match_input():
    result = bursts_per_repo({"alpha": _REPO_A, "beta": _REPO_B})
    assert set(result.keys()) == {"alpha", "beta"}


def test_bursts_per_repo_detects_burst_in_repo_a():
    result = bursts_per_repo({"alpha": _REPO_A})
    assert result["alpha"].total_burst_days >= 1


def test_bursts_per_repo_no_burst_uniform_repo():
    result = bursts_per_repo({"beta": _REPO_B})
    # uniform distribution — no burst
    assert result["beta"].total_burst_days == 0


def test_combined_burst_merges_all_commits():
    report = combined_burst({"alpha": _REPO_A, "beta": _REPO_B})
    total = len(_REPO_A) + len(_REPO_B)
    # average_daily * number_of_unique_days >= total
    from datetime import date
    unique_days = {c.date.date() for c in _REPO_A + _REPO_B}
    assert abs(report.average_daily * len(unique_days) - total) < 0.01


def test_combined_burst_empty_input():
    report = combined_burst({})
    assert report.total_burst_days == 0
    assert report.peak is None


def test_burst_report_dict_structure():
    from gitlog_digest.commit_burst import build_burst_report
    report = build_burst_report(_REPO_A)
    d = burst_report_dict(report)
    assert "average_daily" in d
    assert "total_burst_days" in d
    assert "bursts" in d
    assert isinstance(d["bursts"], list)


def test_burst_report_dict_peak_none_when_no_burst():
    from gitlog_digest.commit_burst import build_burst_report
    report = build_burst_report(_REPO_B)
    d = burst_report_dict(report)
    assert d["peak"] is None


def test_format_all_burst_reports_contains_repo_names():
    text = format_all_burst_reports({"alpha": _REPO_A, "beta": _REPO_B})
    assert "alpha" in text
    assert "beta" in text


def test_format_all_burst_reports_single_repo_no_combined_section():
    text = format_all_burst_reports({"only": _REPO_A})
    assert "combined" not in text
