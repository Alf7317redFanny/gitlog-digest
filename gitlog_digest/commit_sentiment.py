"""Analyse the sentiment/tone of commit messages using simple keyword heuristics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from gitlog_digest.git_reader import GitCommit

_POSITIVE_WORDS = {
    "add", "added", "adds", "improve", "improved", "fix", "fixed", "fixes",
    "enhance", "enhanced", "optimise", "optimised", "optimize", "optimized",
    "clean", "refactor", "simplify", "upgrade", "support",
}

_NEGATIVE_WORDS = {
    "revert", "reverted", "remove", "removed", "delete", "deleted",
    "break", "broken", "hack", "hotfix", "workaround", "ugly", "temp",
    "temporary", "disable", "disabled", "deprecate", "deprecated",
}


def _classify(message: str) -> str:
    tokens = set(message.lower().split())
    pos = len(tokens & _POSITIVE_WORDS)
    neg = len(tokens & _NEGATIVE_WORDS)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


@dataclass
class CommitSentimentReport:
    positive: List[GitCommit] = field(default_factory=list)
    negative: List[GitCommit] = field(default_factory=list)
    neutral: List[GitCommit] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.positive) + len(self.negative) + len(self.neutral)

    @property
    def positive_ratio(self) -> float:
        if self.total == 0:
            return 0.0
        return len(self.positive) / self.total

    @property
    def negative_ratio(self) -> float:
        if self.total == 0:
            return 0.0
        return len(self.negative) / self.total

    def summary_dict(self) -> Dict[str, int]:
        return {
            "positive": len(self.positive),
            "negative": len(self.negative),
            "neutral": len(self.neutral),
        }


def build_sentiment_report(commits: List[GitCommit]) -> CommitSentimentReport:
    report = CommitSentimentReport()
    for commit in commits:
        tone = _classify(commit.subject)
        if tone == "positive":
            report.positive.append(commit)
        elif tone == "negative":
            report.negative.append(commit)
        else:
            report.neutral.append(commit)
    return report


def format_sentiment_report(report: CommitSentimentReport) -> str:
    lines = ["## Commit Sentiment"]
    if report.total == 0:
        lines.append("  No commits.")
        return "\n".join(lines)
    lines.append(f"  Positive : {len(report.positive):>4}  ({report.positive_ratio:.0%})")
    lines.append(f"  Negative : {len(report.negative):>4}  ({report.negative_ratio:.0%})")
    lines.append(f"  Neutral  : {len(report.neutral):>4}")
    return "\n".join(lines)
