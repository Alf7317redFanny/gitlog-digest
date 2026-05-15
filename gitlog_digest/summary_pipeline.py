"""summary_pipeline.py

Orchestrates the full digest pipeline: reads commits, applies filters,
computes stats, builds reports, and assembles everything into a single
result object ready for rendering or export.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .git_reader import read_commits, get_repo_name
from .week_range import WeekRange
from .filters import CommitFilter, apply_filter
from .stats import CommitStats, compute_stats
from .changelog import Changelog, build_changelog
from .tag_parser import TagSummary, parse_commit
from .diff_stats import DiffSummary, build_diff_summary
from .contributor_summary import ContributorSummary
from .streak import compute_streaks
from .milestone_tracker import MilestoneReport
from .activity_heatmap import ActivityHeatmap, build_heatmap
from .commit_frequency import CommitFrequency, build_frequency


@dataclass
class RepoPipelineResult:
    """All computed artefacts for a single repository."""

    repo_path: Path
    repo_name: str
    week: WeekRange
    stats: CommitStats
    changelog: "Changelog"
    tag_summary: TagSummary
    diff_summary: DiffSummary
    heatmap: ActivityHeatmap
    frequency: CommitFrequency


@dataclass
class PipelineResult:
    """Aggregated results across all repositories for a given week."""

    week: WeekRange
    repos: List[RepoPipelineResult] = field(default_factory=list)
    contributor_summary: Optional[ContributorSummary] = None
    milestone_report: Optional[MilestoneReport] = None

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def total_commits(self) -> int:
        return sum(r.stats.total for r in self.repos)

    @property
    def repo_names(self) -> List[str]:
        return [r.repo_name for r in self.repos]


def _process_repo(
    repo_path: Path,
    week: WeekRange,
    commit_filter: Optional[CommitFilter],
) -> RepoPipelineResult:
    """Read and process commits for a single repository."""

    raw_commits = read_commits(repo_path, since=week.start, until=week.end)

    commits = apply_filter(raw_commits, commit_filter) if commit_filter else raw_commits

    stats = compute_stats(commits)
    changelog = build_changelog(commits)
    tag_summary = TagSummary(tagged=[parse_commit(c) for c in commits])
    diff_summary = build_diff_summary(repo_path, commits)
    heatmap = build_heatmap(commits)
    frequency = build_frequency(commits)

    return RepoPipelineResult(
        repo_path=repo_path,
        repo_name=get_repo_name(repo_path),
        week=week,
        stats=stats,
        changelog=changelog,
        tag_summary=tag_summary,
        diff_summary=diff_summary,
        heatmap=heatmap,
        frequency=frequency,
    )


def run_pipeline(
    repo_paths: List[Path],
    week: WeekRange,
    commit_filter: Optional[CommitFilter] = None,
    milestone_thresholds: Optional[List[int]] = None,
) -> PipelineResult:
    """Run the full summary pipeline across all supplied repositories.

    Args:
        repo_paths: Filesystem paths to each git repository.
        week: The week range to summarise.
        commit_filter: Optional filter (author allow-list, merge exclusion, …).
        milestone_thresholds: Commit-count milestones to check (e.g. [100, 500]).

    Returns:
        A :class:`PipelineResult` containing per-repo and aggregate data.
    """

    result = PipelineResult(week=week)

    contributor_summary = ContributorSummary()
    milestone_report = MilestoneReport(thresholds=milestone_thresholds or [])

    for path in repo_paths:
        repo_result = _process_repo(path, week, commit_filter)
        result.repos.append(repo_result)

        # Feed each repo's commits into cross-repo aggregators.
        all_commits = list(repo_result.changelog.all_commits())
        for commit in all_commits:
            contributor_summary.add(repo_result.repo_name, commit)

        if milestone_thresholds:
            milestone_report.add(repo_result.repo_name, repo_result.stats.total)

    result.contributor_summary = contributor_summary
    result.milestone_report = milestone_report if milestone_thresholds else None

    return result
