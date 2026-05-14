"""Tests for the CLI argument parsing and week resolution."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from gitlog_digest.cli import parse_args, resolve_week
from gitlog_digest.week_range import WeekRange
from datetime import date


def test_parse_args_single_repo():
    args = parse_args(["/some/repo"])
    assert args.repos == ["/some/repo"]
    assert not args.current_week
    assert args.week_of is None
    assert args.output is None


def test_parse_args_multiple_repos():
    args = parse_args(["/repo1", "/repo2", "/repo3"])
    assert args.repos == ["/repo1", "/repo2", "/repo3"]


def test_parse_args_current_week_flag():
    args = parse_args([".", "--current-week"])
    assert args.current_week is True


def test_parse_args_week_of():
    args = parse_args([".", "--week-of", "2024-03-11"])
    assert args.week_of == "2024-03-11"


def test_parse_args_output_flag():
    args = parse_args([".", "--output", "digest.md"])
    assert args.output == "digest.md"


def test_mutually_exclusive_week_flags():
    with pytest.raises(SystemExit):
        parse_args([".", "--current-week", "--week-of", "2024-03-11"])


def test_resolve_week_defaults_to_previous():
    args = parse_args(["."])
    from gitlog_digest.week_range import previous_week
    expected = previous_week()
    result = resolve_week(args)
    assert result.start == expected.start
    assert result.end == expected.end


def test_resolve_week_current():
    args = parse_args([".", "--current-week"])
    from gitlog_digest.week_range import current_week
    expected = current_week()
    result = resolve_week(args)
    assert result.start == expected.start


def test_resolve_week_of_specific_date():
    args = parse_args([".", "--week-of", "2024-03-13"])
    result = resolve_week(args)
    # 2024-03-13 is a Wednesday; week should start on Monday 2024-03-11
    assert result.start == date(2024, 3, 11)
    assert result.end == date(2024, 3, 17)


def test_main_missing_git_dir(tmp_path):
    from gitlog_digest.cli import main
    with pytest.raises(SystemExit) as exc_info:
        main([str(tmp_path)])
    assert exc_info.value.code == 1
