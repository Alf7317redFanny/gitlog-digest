"""Tests for gitlog_digest.export."""

from __future__ import annotations

import csv
import io
import json
from datetime import date, datetime

import pytest

from gitlog_digest.digest import Digest, RepoSummary
from gitlog_digest.export import export_csv, export_digest, export_json
from gitlog_digest.git_reader import GitCommit
from gitlog_digest.week_range import WeekRange


def _make_commit(sha: str, author: str, subject: str, day: int = 1) -> GitCommit:
    return GitCommit(
        sha=sha,
        author=author,
        date=datetime(2024, 4, day, 12, 0, 0),
        subject=subject,
    )


def _make_digest() -> Digest:
    commits_a = [
        _make_commit("aaa1111", "Alice", "feat: add login", day=1),
        _make_commit("bbb2222", "Bob", "fix: typo", day=2),
    ]
    commits_b = [
        _make_commit("ccc3333", "Alice", "chore: update deps", day=3),
    ]
    week = WeekRange.containing(date(2024, 4, 1))
    repos = [
        RepoSummary(name="repo-alpha", commits=commits_a),
        RepoSummary(name="repo-beta", commits=commits_b),
    ]
    return Digest(week=week, repos=repos)


# --- JSON export ---

def test_export_json_is_valid_json():
    digest = _make_digest()
    result = export_json(digest)
    data = json.loads(result)  # must not raise
    assert isinstance(data, dict)


def test_export_json_contains_week():
    digest = _make_digest()
    data = json.loads(export_json(digest))
    assert "week" in data
    assert "2024" in data["week"]


def test_export_json_total_commits():
    digest = _make_digest()
    data = json.loads(export_json(digest))
    assert data["total_commits"] == 3


def test_export_json_repo_names():
    digest = _make_digest()
    data = json.loads(export_json(digest))
    names = [r["repo"] for r in data["repos"]]
    assert "repo-alpha" in names
    assert "repo-beta" in names


def test_export_json_commit_fields():
    digest = _make_digest()
    data = json.loads(export_json(digest))
    commit = data["repos"][0]["commits"][0]
    assert "sha" in commit
    assert "author" in commit
    assert "date" in commit
    assert "subject" in commit


# --- CSV export ---

def test_export_csv_has_header():
    digest = _make_digest()
    result = export_csv(digest)
    reader = csv.DictReader(io.StringIO(result))
    assert set(reader.fieldnames or []) == {"week", "repo", "sha", "author", "date", "subject"}


def test_export_csv_row_count():
    digest = _make_digest()
    result = export_csv(digest)
    rows = list(csv.DictReader(io.StringIO(result)))
    assert len(rows) == 3


def test_export_csv_repo_column():
    digest = _make_digest()
    result = export_csv(digest)
    rows = list(csv.DictReader(io.StringIO(result)))
    repos = {r["repo"] for r in rows}
    assert repos == {"repo-alpha", "repo-beta"}


# --- dispatch ---

def test_export_digest_json():
    digest = _make_digest()
    result = export_digest(digest, "json")
    json.loads(result)  # valid JSON


def test_export_digest_csv():
    digest = _make_digest()
    result = export_digest(digest, "csv")
    assert "repo" in result.splitlines()[0]


def test_export_digest_unknown_format():
    digest = _make_digest()
    with pytest.raises(ValueError, match="Unsupported"):
        export_digest(digest, "xml")  # type: ignore[arg-type]
