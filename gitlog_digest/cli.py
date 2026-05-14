"""Command-line interface for gitlog-digest."""

import argparse
import sys
from pathlib import Path

from gitlog_digest.digest import build_digest
from gitlog_digest.formatter import format_digest
from gitlog_digest.week_range import WeekRange, current_week, previous_week


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="gitlog-digest",
        description="Generate a weekly summary of git activity across repositories.",
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
        help="Summarise commits from the current week (default: previous week).",
    )
    week_group.add_argument(
        "--week-of",
        metavar="DATE",
        help="Summarise commits from the week containing DATE (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    return parser.parse_args(argv)


def resolve_week(args) -> WeekRange:
    if args.week_of:
        from datetime import date
        from gitlog_digest.week_range import week_containing
        target = date.fromisoformat(args.week_of)
        return week_containing(target)
    if args.current_week:
        return current_week()
    return previous_week()


def main(argv=None):
    args = parse_args(argv)
    week = resolve_week(args)

    repo_paths = [Path(r) for r in args.repos]
    for path in repo_paths:
        if not (path / ".git").exists():
            print(f"error: '{path}' does not appear to be a git repository.", file=sys.stderr)
            sys.exit(1)

    digest = build_digest(repo_paths, week)
    output = format_digest(digest)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Digest written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
