"""Integration tests for hotspot_integration module."""
from __future__ import annotations

from datetime import datetime, timezone

from gitlog_digest.commit_hotspot import build_hotspot_report
from gitlog_digest.hotspot_integration import (
    combined_hotspot,
    format_all_hotspot_reports,
    hotspot_report_dict,
    hotspots_per_repo,
)
from gitlog_digest.git_reader import GitCommit


def _c(files: list[str], msg: str = "fix: patch") -> GitCommit:
    return GitCommit(
        sha="deadbeef",
        short_sha="deadbee",
        subject=msg,
        author="Alice",
        date=datetime(2024, 4, 1, tzinfo=timezone.utc),
        files_changed=files,
        insertions=2,
        deletions=1,
        branch="main",
    )


def test_hotspots_per_repo_keys_match_input():
    data = {"repo-a": [_c(["a.py"])], "repo-b": [_c(["b.py"])]}
    result = hotspots_per_repo(data)
    assert set(result.keys()) == {"repo-a", "repo-b"}


def test_hotspots_per_repo_totals():
    data = {"repo-a": [_c(["x.py", "y.py"]), _c(["x.py"])]}
    result = hotspots_per_repo(data)
    assert result["repo-a"].peak().path == "x.py"
    assert result["repo-a"].peak().count == 2


def test_combined_hotspot_merges_all_commits():
    data = {
        "repo-a": [_c(["shared.py"]), _c(["shared.py"])],
        "repo-b": [_c(["shared.py"])],
    }
    report = combined_hotspot(data)
    assert report.peak().path == "shared.py"
    assert report.peak().count == 3


def test_combined_hotspot_empty_input():
    report = combined_hotspot({})
    assert report.total_files() == 0


def test_hotspot_report_dict_structure():
    report = build_hotspot_report([_c(["main.py", "utils.py"]), _c(["main.py"])])
    d = hotspot_report_dict(report, top_n=5)
    assert "total_files" in d
    assert "peak_file" in d
    assert "hotspots" in d
    assert d["total_files"] == 2
    assert d["hotspots"][0]["path"] == "main.py"


def test_hotspot_report_dict_empty():
    report = build_hotspot_report([])
    d = hotspot_report_dict(report)
    assert d["peak_file"] is None
    assert d["hotspots"] == []


def test_format_all_hotspot_reports_contains_repo_names():
    data = {"my-repo": [_c(["app.py"])]}
    text = format_all_hotspot_reports(data)
    assert "my-repo" in text
    assert "Combined" in text
