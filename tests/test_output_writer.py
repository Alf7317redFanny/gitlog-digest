"""Tests for gitlog_digest.output_writer."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from gitlog_digest.output_writer import build_output_filename, write_output


SAMPLE_CONTENT = "# Weekly Digest\n\nSome commits happened.\n"


def test_write_output_stdout(capsys):
    write_output(SAMPLE_CONTENT)
    captured = capsys.readouterr()
    assert captured.out == SAMPLE_CONTENT


def test_write_output_stdout_adds_newline_if_missing(capsys):
    write_output("no newline at end")
    captured = capsys.readouterr()
    assert captured.out.endswith("\n")


def test_write_output_to_file(tmp_path):
    output_file = tmp_path / "digest.md"
    write_output(SAMPLE_CONTENT, str(output_file))
    assert output_file.read_text(encoding="utf-8") == SAMPLE_CONTENT


def test_write_output_creates_parent_dirs(tmp_path):
    nested = tmp_path / "reports" / "2024" / "digest.md"
    write_output(SAMPLE_CONTENT, str(nested))
    assert nested.exists()
    assert nested.read_text(encoding="utf-8") == SAMPLE_CONTENT


def test_write_output_to_file_prints_confirmation(tmp_path, capsys):
    output_file = tmp_path / "out.md"
    write_output(SAMPLE_CONTENT, str(output_file))
    captured = capsys.readouterr()
    assert str(output_file) in captured.err


@pytest.mark.parametrize(
    "label, extension, expected",
    [
        ("2024-W03", "md", "digest-2024-W03.md"),
        ("2024-W03", "txt", "digest-2024-W03.txt"),
        ("week of 2024-01-15", "md", "digest-week-of-2024-01-15.md"),
    ],
)
def test_build_output_filename(label, extension, expected):
    assert build_output_filename(label, extension) == expected


def test_build_output_filename_default_extension():
    result = build_output_filename("2024-W10")
    assert result.endswith(".md")
