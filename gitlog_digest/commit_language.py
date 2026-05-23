"""Detect probable programming language from changed file extensions."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from gitlog_digest.git_reader import GitCommit

_EXT_TO_LANG: dict[str, str] = {
    "py": "Python",
    "js": "JavaScript",
    "ts": "TypeScript",
    "jsx": "JavaScript",
    "tsx": "TypeScript",
    "rb": "Ruby",
    "go": "Go",
    "rs": "Rust",
    "java": "Java",
    "kt": "Kotlin",
    "cs": "C#",
    "cpp": "C++",
    "c": "C",
    "h": "C",
    "hpp": "C++",
    "swift": "Swift",
    "php": "PHP",
    "scala": "Scala",
    "sh": "Shell",
    "bash": "Shell",
    "zsh": "Shell",
    "html": "HTML",
    "css": "CSS",
    "scss": "CSS",
    "sass": "CSS",
    "sql": "SQL",
    "r": "R",
    "lua": "Lua",
    "ex": "Elixir",
    "exs": "Elixir",
    "hs": "Haskell",
    "clj": "Clojure",
    "dart": "Dart",
}


def _detect_language(filename: str) -> Optional[str]:
    """Return the language name for a filename, or None if unrecognised."""
    if "." not in filename:
        return None
    ext = filename.rsplit(".", 1)[-1].lower()
    return _EXT_TO_LANG.get(ext)


@dataclass
class LanguageEntry:
    language: str
    commit_count: int = 0
    file_count: int = 0

    def __str__(self) -> str:
        return f"{self.language}: {self.commit_count} commits, {self.file_count} files touched"


@dataclass
class CommitLanguageReport:
    _entries: dict[str, LanguageEntry] = field(default_factory=dict)

    def add_commit(self, commit: GitCommit) -> None:
        seen: set[str] = set()
        for filename in commit.files_changed:
            lang = _detect_language(filename)
            if lang is None:
                continue
            if lang not in self._entries:
                self._entries[lang] = LanguageEntry(language=lang)
            self._entries[lang].file_count += 1
            seen.add(lang)
        for lang in seen:
            self._entries[lang].commit_count += 1

    def top(self, n: int = 5) -> List[LanguageEntry]:
        return sorted(self._entries.values(), key=lambda e: e.commit_count, reverse=True)[:n]

    def languages(self) -> List[str]:
        return list(self._entries.keys())

    def entry_for(self, language: str) -> Optional[LanguageEntry]:
        return self._entries.get(language)

    def __len__(self) -> int:
        return len(self._entries)


def build_language_report(commits: Iterable[GitCommit]) -> CommitLanguageReport:
    report = CommitLanguageReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def merge_reports(*reports: CommitLanguageReport) -> CommitLanguageReport:
    merged = CommitLanguageReport()
    for report in reports:
        for entry in report._entries.values():
            if entry.language not in merged._entries:
                merged._entries[entry.language] = LanguageEntry(language=entry.language)
            merged._entries[entry.language].commit_count += entry.commit_count
            merged._entries[entry.language].file_count += entry.file_count
    return merged
