"""Command-line interface for gitlog-digest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from gitlog_digest.digest import Digest, RepoSummary
from gitlog_digest.formatter import format_digest
from gitlog_digest.git_reader import get_repo_name, read_commits
from gitlog_digest.output_writer import build_output_filename, write_output
from gitlog_digest.week_range import WeekRange, current_week, previous_week, week_containing


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gitlog-digest",
        description="Generate a concise weekly summary of git activity.",
    )
    parser.add_argument(
        "repos",
        nargs="+",
        metavar="REPO",
        help="Path(s) to git repository/repositories.",
    )
    week_group = parser.add_mutually_exclusive_group()
    week_group.add_argument(
        "--current-week",
        action="store_true",
        default=False,
        help="Summarise the current (in-progress) week.",
    )
    week_group.add_argument(
        "--week-of",
        metavar="DATE",
        help="Summarise the week containing DATE (YYYY-MM-DD).",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--auto-name",
        action="store_true",
        default=False,
        help="Auto-generate output filename from the week label (implies --output).",
    )
    return parser.parse_args(argv)


def resolve_week(args: argparse.Namespace) -> WeekRange:
    if args.current_week:
        return current_week()
    if args.week_of:
        from datetime import date
        year, month, day = (int(p) for p in args.week_of.split("-"))
        return week_containing(date(year, month, day))
    return previous_week()


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    week = resolve_week(args)

    summaries = []
    for repo_path in args.repos:
        path = Path(repo_path)
        if not path.exists():
            print(f"error: repository path does not exist: {path}", file=sys.stderr)
            return 1
        commits = read_commits(path, week.start, week.end)
        summaries.append(RepoSummary(name=get_repo_name(path), commits=commits))

    digest = Digest(week=week, repos=summaries)
    content = format_digest(digest)

    output_path = args.output
    if args.auto_name and output_path is None:
        output_path = build_output_filename(week.label)

    write_output(content, output_path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
