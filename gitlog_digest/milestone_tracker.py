"""Track commit milestones (e.g. round-number commits) across repos."""

from dataclasses import dataclass, field
from typing import List, Optional

DEFAULT_MILESTONES = [10, 25, 50, 100, 250, 500, 1000]


@dataclass
class MilestoneHit:
    repo: str
    milestone: int
    actual_count: int
    sha: str
    author: str
    subject: str

    def __str__(self) -> str:
        return (
            f"[{self.repo}] reached {self.milestone} commits "
            f"(total: {self.actual_count}) — {self.sha[:7]} by {self.author}: {self.subject}"
        )


@dataclass
class MilestoneReport:
    hits: List[MilestoneHit] = field(default_factory=list)

    def add(self, hit: MilestoneHit) -> None:
        self.hits.append(hit)

    @property
    def total(self) -> int:
        return len(self.hits)

    def for_repo(self, repo: str) -> List[MilestoneHit]:
        return [h for h in self.hits if h.repo == repo]


def check_milestones(
    repo: str,
    commits: list,
    baseline: int = 0,
    thresholds: Optional[List[int]] = None,
) -> MilestoneReport:
    """Return a MilestoneReport for any milestones crossed between baseline
    and baseline + len(commits)."""
    if thresholds is None:
        thresholds = DEFAULT_MILESTONES

    report = MilestoneReport()
    new_total = baseline + len(commits)

    for threshold in thresholds:
        if baseline < threshold <= new_total:
            # Find the commit that pushed us over
            offset = threshold - baseline  # 1-based index into commits
            commit = commits[offset - 1]
            report.add(
                MilestoneHit(
                    repo=repo,
                    milestone=threshold,
                    actual_count=new_total,
                    sha=commit.sha,
                    author=commit.author,
                    subject=commit.subject,
                )
            )

    return report


def format_milestone_report(report: MilestoneReport) -> str:
    """Render a milestone report as a plain-text block."""
    if not report.hits:
        return "No milestones reached this period."

    lines = ["## Milestones", ""]
    for hit in report.hits:
        lines.append(f"  * {hit}")
    lines.append("")
    return "\n".join(lines)
