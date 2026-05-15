"""Tests for gitlog_digest.graph_integration."""
from datetime import datetime, timezone

import pytest

from gitlog_digest.git_reader import GitCommit
from gitlog_digest.graph_integration import (
    combined_graph,
    format_all_graph_reports,
    graph_report_dict,
    graphs_per_repo,
)


def _c(day: str, author: str = "alice") -> GitCommit:
    dt = datetime.fromisoformat(f"{day}T09:00:00").replace(tzinfo=timezone.utc)
    return GitCommit(sha="aabbcc", author=author, date=dt, message="test")


REPO_COMMITS = {
    "alpha": [_c("2024-03-04"), _c("2024-03-05")],
    "beta": [_c("2024-03-05"), _c("2024-03-06"), _c("2024-03-06")],
}


def test_graphs_per_repo_keys_match_input():
    graphs = graphs_per_repo(REPO_COMMITS)
    assert set(graphs.keys()) == {"alpha", "beta"}


def test_graphs_per_repo_totals():
    graphs = graphs_per_repo(REPO_COMMITS)
    assert graphs["alpha"].total == 2
    assert graphs["beta"].total == 3


def test_combined_graph_total():
    graph = combined_graph(REPO_COMMITS)
    assert graph.total == 5


def test_combined_graph_peak_day():
    graph = combined_graph(REPO_COMMITS)
    # 2024-03-05 has 1+1=2, 2024-03-06 has 2 — tied; max picks last max
    assert graph.peak_day is not None


def test_combined_graph_empty():
    graph = combined_graph({})
    assert graph.total == 0
    assert graph.peak_day is None


def test_graph_report_dict_structure():
    report = graph_report_dict(REPO_COMMITS)
    assert "repos" in report
    assert "combined" in report
    assert "alpha" in report["repos"]
    assert "beta" in report["repos"]


def test_graph_report_dict_rows_sorted():
    report = graph_report_dict(REPO_COMMITS)
    alpha_rows = report["repos"]["alpha"]["rows"]
    days = [r["day"] for r in alpha_rows]
    assert days == sorted(days)


def test_graph_report_dict_combined_total():
    report = graph_report_dict(REPO_COMMITS)
    assert report["combined"]["total"] == 5


def test_format_all_graph_reports_contains_repo_names():
    output = format_all_graph_reports(REPO_COMMITS)
    assert "alpha" in output
    assert "beta" in output


def test_format_all_graph_reports_contains_combined_when_multiple():
    output = format_all_graph_reports(REPO_COMMITS)
    assert "Combined" in output


def test_format_all_graph_reports_no_combined_for_single_repo():
    output = format_all_graph_reports({"alpha": REPO_COMMITS["alpha"]})
    assert "Combined" not in output
