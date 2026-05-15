"""Extracts keyword frequency from commit messages for a simple word cloud."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

from gitlog_digest.git_reader import GitCommit

_STOP_WORDS = frozenset(
    {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "was", "are", "be", "been", "this",
        "that", "it", "as", "not", "no", "so", "if", "up", "do", "did",
    }
)


def _tokenise(message: str) -> List[str]:
    """Lower-case and split a commit message into meaningful tokens."""
    tokens = re.findall(r"[a-zA-Z]{3,}", message.lower())
    return [t for t in tokens if t not in _STOP_WORDS]


@dataclass
class WordCloudReport:
    """Holds word frequency counts built from commit messages."""

    counts: Counter = field(default_factory=Counter)

    def top(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return the *n* most common words."""
        return self.counts.most_common(n)

    @property
    def total_words(self) -> int:
        return sum(self.counts.values())

    def __len__(self) -> int:
        return len(self.counts)


def build_word_cloud(commits: Iterable[GitCommit]) -> WordCloudReport:
    """Build a WordCloudReport from an iterable of commits."""
    report = WordCloudReport()
    for commit in commits:
        for token in _tokenise(commit.subject):
            report.counts[token] += 1
    return report


def word_cloud_dict(report: WordCloudReport, top_n: int = 10) -> Dict:
    """Serialise the report to a plain dict suitable for JSON export."""
    return {
        "total_unique_words": len(report),
        "total_word_occurrences": report.total_words,
        "top_words": [{"word": w, "count": c} for w, c in report.top(top_n)],
    }


def format_word_cloud_text(report: WordCloudReport, top_n: int = 10) -> str:
    """Return a human-readable word-frequency section."""
    lines = ["## Commit Message Keywords", ""]
    top = report.top(top_n)
    if not top:
        lines.append("  (no data)")
    else:
        max_count = top[0][1]
        bar_width = 20
        for word, count in top:
            bar = "#" * max(1, round(count / max_count * bar_width))
            lines.append(f"  {word:<20} {bar:<20} {count}")
    lines.append("")
    return "\n".join(lines)
