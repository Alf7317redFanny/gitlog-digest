"""Classify commits by domain/area based on file paths touched."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Optional

from gitlog_digest.git_reader import GitCommit

_DOMAIN_MAP = {
    "test": ["test", "tests", "spec", "__tests__"],
    "docs": ["docs", "doc", "documentation", "readme"],
    "ci": [".github", "ci", ".circleci", ".travis"],
    "config": ["config", "conf", "settings", ".env"],
    "frontend": ["frontend", "ui", "client", "web", "src/components", "src/pages"],
    "backend": ["backend", "server", "api", "src/api", "src/server"],
    "data": ["data", "migrations", "db", "database", "schema"],
    "scripts": ["scripts", "bin", "tools"],
}


def _detect_domain(files: List[str]) -> Optional[str]:
    """Return the most prominent domain for the given file list."""
    counts: dict[str, int] = defaultdict(int)
    for f in files:
        lower = f.lower()
        for domain, patterns in _DOMAIN_MAP.items():
            if any(lower.startswith(p + "/") or "/" + p + "/" in lower or lower == p for p in patterns):
                counts[domain] += 1
                break
    if not counts:
        return None
    return max(counts, key=lambda d: counts[d])


@dataclass
class DomainEntry:
    domain: str
    count: int = 0

    def __str__(self) -> str:
        return f"{self.domain}: {self.count} commit(s)"


@dataclass
class CommitDomainReport:
    _entries: dict[str, DomainEntry] = field(default_factory=dict)
    unclassified: int = 0

    def add_commit(self, commit: GitCommit) -> None:
        domain = _detect_domain(commit.files_changed)
        if domain is None:
            self.unclassified += 1
        else:
            if domain not in self._entries:
                self._entries[domain] = DomainEntry(domain=domain)
            self._entries[domain].count += 1

    def total(self) -> int:
        return sum(e.count for e in self._entries.values()) + self.unclassified

    def top(self, n: int = 5) -> List[DomainEntry]:
        return sorted(self._entries.values(), key=lambda e: e.count, reverse=True)[:n]

    def domains(self) -> List[str]:
        return list(self._entries.keys())

    def count_for(self, domain: str) -> int:
        return self._entries[domain].count if domain in self._entries else 0


def build_domain_report(commits: List[GitCommit]) -> CommitDomainReport:
    report = CommitDomainReport()
    for commit in commits:
        report.add_commit(commit)
    return report


def domain_report_dict(report: CommitDomainReport) -> dict:
    return {
        "total": report.total(),
        "unclassified": report.unclassified,
        "domains": [
            {"domain": e.domain, "count": e.count}
            for e in report.top()
        ],
    }
