"""Write exported digest data (JSON/CSV) to a file or stdout."""

from __future__ import annotations

import sys
from pathlib import Path

from gitlog_digest.digest import Digest
from gitlog_digest.export import ExportFormat, export_digest
from gitlog_digest.week_range import WeekRange


def _default_filename(week: WeekRange, fmt: ExportFormat) -> str:
    """Build a sensible default filename from the week label and format."""
    safe_label = str(week).replace(" ", "_").replace("/", "-")
    return f"digest_{safe_label}.{fmt}"


def write_export(
    digest: Digest,
    fmt: ExportFormat,
    output: str | Path | None = None,
    *,
    print_confirmation: bool = True,
) -> None:
    """Export *digest* in *fmt* and write to *output* (or stdout if None).

    Parameters
    ----------
    digest:
        The digest to export.
    fmt:
        ``"json"`` or ``"csv"``.
    output:
        Destination file path.  When *None* the result is written to stdout.
    print_confirmation:
        When writing to a file, print a short confirmation message to stderr.
    """
    content = export_digest(digest, fmt)

    if output is None:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
        return

    dest = Path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")

    if print_confirmation:
        print(f"Exported {fmt.upper()} digest → {dest}", file=sys.stderr)


def write_export_auto(
    digest: Digest,
    fmt: ExportFormat,
    directory: str | Path = ".",
    *,
    print_confirmation: bool = True,
) -> Path:
    """Export *digest* to an auto-named file inside *directory*.

    Returns the path of the written file.
    """
    filename = _default_filename(digest.week, fmt)
    dest = Path(directory) / filename
    write_export(digest, fmt, dest, print_confirmation=print_confirmation)
    return dest
