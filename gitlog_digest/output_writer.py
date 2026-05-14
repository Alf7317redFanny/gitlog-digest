"""Handles writing digest output to various destinations (stdout, file)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional


def write_output(content: str, output_path: Optional[str] = None) -> None:
    """Write content to stdout or a file depending on output_path.

    Args:
        content: The formatted digest string to write.
        output_path: If provided, write to this file path. Otherwise use stdout.
    """
    if output_path is None:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
        return

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    print(f"Digest written to {destination}", file=sys.stderr)


def build_output_filename(week_label: str, extension: str = "md") -> str:
    """Generate a sensible default filename from a week label.

    Example:
        >>> build_output_filename("2024-W03")
        'digest-2024-W03.md'
    """
    safe_label = week_label.replace(" ", "-").replace("/", "-")
    return f"digest-{safe_label}.{extension}"
