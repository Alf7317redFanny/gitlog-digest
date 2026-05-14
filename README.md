# gitlog-digest

Generates concise weekly summaries of git activity across multiple repositories in a human-readable format.

## Installation

```bash
pip install gitlog-digest
```

## Usage

Run `gitlog-digest` from any directory containing git repositories, or pass paths explicitly:

```bash
# Summarize all repos in the current directory
gitlog-digest

# Summarize specific repositories
gitlog-digest --repos ~/projects/api ~/projects/frontend

# Specify a custom time range (default: last 7 days)
gitlog-digest --since "2 weeks ago"

# Output to a file
gitlog-digest --output summary.md
```

**Example output:**

```
Weekly Git Digest — 2024-01-08 to 2024-01-14

📁 api (23 commits)
  - Refactored authentication middleware
  - Added rate limiting to public endpoints
  - Fixed token expiration bug (#412)

📁 frontend (11 commits)
  - Migrated components to TypeScript
  - Improved mobile responsiveness on dashboard
```

## Configuration

Create a `.gitlog-digest.toml` in your home directory to set defaults:

```toml
repos = ["~/projects/api", "~/projects/frontend"]
since = "1 week ago"
output = "~/digests"
```

## Requirements

- Python 3.8+
- Git installed and available on `PATH`

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

## License

MIT