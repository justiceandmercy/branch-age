# branch-age

List git branches by the age of their last commit, and prune the stale ones.

A tiny, dependency-free CLI for cleaning up local (or remote) branches that nobody
has touched in months. Sorts branches newest-first, color-codes age, and can
delete stale branches interactively.

## Features

- Lists branches with last-commit date, author, and age in days.
- Color-coded age (green < 90d, yellow < 180d, red >= 180d).
- Filter with `--stale DAYS` to show only old branches.
- Inspect remote-tracking branches with `--remote`.
- Interactive deletion with confirmation; `--yes` for scripting.
- `--force` to delete unmerged branches.
- Works on any git repo; no third-party dependencies.

## Install

```sh
pip install -e .
```

Or run directly:

```sh
python -m branch_age
```

## Usage

```sh
# list all local branches by age
branch-age

# only branches older than 90 days
branch-age --stale 90

# remote branches
branch-age --remote --stale 180

# delete stale branches (interactive)
branch-age --stale 180 --delete

# non-interactive
branch-age --stale 180 --delete --yes --force
```

Sample output:

```
BRANCH                                   AGE  LAST COMMIT              SUBJECT
main *                                   2d   2026-10-17 12:00        bump version
old-feature                            240d  2026-02-21 09:14        wip
```

## License

MIT