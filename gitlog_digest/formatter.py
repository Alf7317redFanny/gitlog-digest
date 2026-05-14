"""Plain-text formatter for a Digest object."""

from .digest import Digest, author_breakdown

SEP = "-" * 60


def format_digest(digest: Digest) -> str:
    """Render a Digest as a human-readable plain-text report."""
    lines: list[str] = []

    lines.append("=" * 60)
    lines.append(f"  Git Activity Digest — {digest.week.label()}")
    lines.append(f"  {digest.week}")
    lines.append("=" * 60)
    lines.append("")

    active = digest.active_repos
    if not active:
        lines.append("No commits found for this week.")
        return "\n".join(lines)

    lines.append(f"Repositories with activity: {len(active)}")
    lines.append(f"Total commits             : {digest.total_commits}")
    lines.append("")

    for repo in active:
        lines.append(SEP)
        lines.append(f"Repo : {repo.name}")
        lines.append(f"Path : {repo.path}")
        lines.append(f"Commits ({repo.commit_count}) | Authors: {', '.join(repo.authors)}")
        lines.append("")
        for commit in repo.commits:
            date_str = commit.date.strftime("%Y-%m-%d %H:%M")
            lines.append(f"  {commit.short_sha}  {date_str}  {commit.author}")
            lines.append(f"          {commit.subject}")
        lines.append("")

    lines.append(SEP)
    lines.append("Author breakdown:")
    for author, count in author_breakdown(digest).items():
        lines.append(f"  {author:<30} {count:>4} commit{'s' if count != 1 else ''}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)
