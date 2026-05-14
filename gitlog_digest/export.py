"""Export digest data to structured formats (JSON, CSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from gitlog_digest.changelog import Changelog
from gitlog_digest.digest import Digest

ExportFormat = Literal["json", "csv"]


def _digest_to_dict(digest: Digest) -> dict:
    """Serialise a Digest to a plain dictionary."""
    repos = []
    for summary in digest.repos:
        repos.append(
            {
                "repo": summary.name,
                "commit_count": summary.commit_count,
                "authors": sorted(summary.authors),
                "commits": [
                    {
                        "sha": c.short_sha,
                        "author": c.author,
                        "date": c.date.isoformat(),
                        "subject": c.subject,
                    }
                    for c in summary.commits
                ],
            }
        )
    return {
        "week": str(digest.week),
        "total_commits": digest.total_commits,
        "repos": repos,
    }


def export_json(digest: Digest, *, indent: int = 2) -> str:
    """Return a JSON string representation of the digest."""
    return json.dumps(_digest_to_dict(digest), indent=indent, default=str)


def export_csv(digest: Digest) -> str:
    """Return a CSV string with one row per commit across all repos."""
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=["week", "repo", "sha", "author", "date", "subject"],
        lineterminator="\n",
    )
    writer.writeheader()
    week_label = str(digest.week)
    for summary in digest.repos:
        for c in summary.commits:
            writer.writerow(
                {
                    "week": week_label,
                    "repo": summary.name,
                    "sha": c.short_sha,
                    "author": c.author,
                    "date": c.date.isoformat(),
                    "subject": c.subject,
                }
            )
    return buf.getvalue()


def export_digest(digest: Digest, fmt: ExportFormat) -> str:
    """Dispatch to the correct exporter based on *fmt*."""
    if fmt == "json":
        return export_json(digest)
    if fmt == "csv":
        return export_csv(digest)
    raise ValueError(f"Unsupported export format: {fmt!r}")
