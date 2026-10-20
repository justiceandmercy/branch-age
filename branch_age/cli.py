"""Command-line interface for branch-age."""

import argparse
import sys
from typing import Optional

from . import __version__
from .git import (
    current_branch,
    delete_branch,
    is_repo,
    list_branches,
)


def _color(text: str, code: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"\033[{code}m{text}\033[0m"


def _age_color(days: int, color: bool) -> str:
    if days >= 180:
        return _color(f"{days}d", "31", color)  # red
    if days >= 90:
        return _color(f"{days}d", "33", color)  # yellow
    return _color(f"{days}d", "32", color)  # green


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="branch-age",
        description="List git branches by last-commit age; prune stale ones.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument(
        "--stale",
        type=int,
        default=None,
        metavar="DAYS",
        help="Only show branches older than DAYS.",
    )
    p.add_argument(
        "--remote",
        action="store_true",
        help="Inspect remote-tracking branches instead of local ones.",
    )
    p.add_argument(
        "--delete",
        action="store_true",
        help="Delete the selected (stale) branches.",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Force-delete even if not merged.",
    )
    p.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt when deleting.",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output.",
    )
    p.add_argument(
        "--cwd",
        default=None,
        help="Repository to operate on (default: current dir).",
    )
    return p


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)
    cwd = args.cwd
    color = not args.no_color and sys.stdout.isatty()

    if not is_repo(cwd):
        print("error: not a git repository", file=sys.stderr)
        return 2

    branches = list_branches(remote=args.remote, cwd=cwd)
    if args.stale is not None:
        branches = [b for b in branches if b["age_days"] >= args.stale]

    if not branches:
        print("No matching branches.")
        return 0

    cur = current_branch(cwd)
    # header
    print(f"{'BRANCH':<40} {'AGE':>8}  {'LAST COMMIT':<20}  SUBJECT")
    for b in branches:
        name = b["name"]
        if name == cur:
            name = _color(name + " *", "1", color)
        age = _age_color(b["age_days"], color)
        date = b["date"].strftime("%Y-%m-%d %H:%M")
        subj = b["subject"][:50]
        print(f"{name:<40} {age:>8}  {date:<20}  {subj}")

    if not args.delete:
        return 0

    targets = [b["name"] for b in branches]
    # never delete the current branch
    if cur in targets:
        targets = [t for t in targets if t != cur]
    if not targets:
        print("Nothing to delete.")
        return 0

    if not args.yes:
        print()
        print("Branches to delete:")
        for t in targets:
            print(f"  - {t}")
        answer = input("Proceed? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("Aborted.")
            return 1

    failed = []
    for t in targets:
        ok = delete_branch(t, remote=args.remote, force=args.force, cwd=cwd)
        status = _color("deleted", "32", color) if ok else _color("FAILED", "31", color)
        print(f"  {t}: {status}")
        if not ok:
            failed.append(t)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())