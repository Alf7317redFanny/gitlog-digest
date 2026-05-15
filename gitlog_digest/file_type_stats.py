"""Aggregate commit activity broken down by file extension."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from gitlog_digest.git_reader import GitCommit


@dataclass
class FileTypeEntry:
    extension: str
    commit_count: int = 0
    authors: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        unique = len(set(self.authors))
        return f"{self.extension or '(none)'}: {self.commit_count} commit(s) by {unique} author(s)"


@dataclass
class FileTypeReport:
    _entries: Dict[str, FileTypeEntry] = field(default_factory=dict)

    @property
    def extensions(self) -> List[str]:
        return sorted(self._entries.keys())

    def entry_for(self, ext: str) -> FileTypeEntry:
        return self._entries.get(ext, FileTypeEntry(extension=ext))

    @property
    def total_extensions(self) -> int:
        return len(self._entries)

    def top(self, n: int = 5) -> List[FileTypeEntry]:
        sorted_entries = sorted(
            self._entries.values(),
            key=lambda e: e.commit_count,
            reverse=True,
        )
        return sorted_entries[:n]


def _extract_extension(filename: str) -> str:
    """Return the lowercase extension (without dot), or empty string."""
    if "." in filename:
        return filename.rsplit(".", 1)[-1].lower()
    return ""


def build_file_type_report(commits: Sequence[GitCommit]) -> FileTypeReport:
    """Build a FileTypeReport from a sequence of commits.

    Each commit's ``files`` attribute (list of changed filenames) is used.
    Falls back gracefully when ``files`` is absent or empty.
    """
    counts: Dict[str, int] = defaultdict(int)
    author_map: Dict[str, List[str]] = defaultdict(list)

    for commit in commits:
        files = getattr(commit, "files", []) or []
        seen_exts = set()
        for filename in files:
            ext = _extract_extension(filename)
            if ext not in seen_exts:
                counts[ext] += 1
                author_map[ext].append(commit.author)
                seen_exts.add(ext)

    entries = {
        ext: FileTypeEntry(extension=ext, commit_count=cnt, authors=author_map[ext])
        for ext, cnt in counts.items()
    }
    return FileTypeReport(_entries=entries)


def file_type_report_dict(report: FileTypeReport) -> dict:
    """Serialise a FileTypeReport to a plain dict."""
    return {
        "total_extensions": report.total_extensions,
        "top": [
            {
                "extension": e.extension or "(none)",
                "commit_count": e.commit_count,
                "unique_authors": len(set(e.authors)),
            }
            for e in report.top()
        ],
    }
