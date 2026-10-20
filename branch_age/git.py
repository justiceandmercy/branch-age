"""Git helpers for branch-age."""

import subprocess
from datetime import datetime, timezone
from typing import List, Optional


def _run(args: List[str], cwd: Optional[str] = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def is_repo(cwd: Optional[str] = None) -> bool:
    try:
        _run(["rev-parse", "--is-inside-work-tree"], cwd=cwd)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def current_branch(cwd: Optional[str] = None) -> Optional[str]:
    try:
        out = _run(["symbolic-ref", "--short", "HEAD"], cwd=cwd).strip()
        return out or None
    except subprocess.CalledProcessError:
        return None


def list_branches(
    remote: bool = False,
    cwd: Optional[str] = None,
) -> List[dict]:
    """Return branches sorted by last commit date (newest first)."""
    ref = "refs/remotes" if remote else "refs/heads"
    fmt = "%(refname:short)\t%(committerdate:iso-strict)\t%(authorname)\t%(subject)"
    out = _run(["for-each-ref", f"--sort=-committerdate", ref, f"--format={fmt}"], cwd=cwd)
    branches = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 3)
        if len(parts) < 2:
            continue
        name = parts[0]
        # skip remote HEAD pseudo-refs
        if name.endswith("/HEAD"):
            continue
        try:
            when = datetime.fromisoformat(parts[1].replace("Z", "+00:00"))
        except ValueError:
            continue
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - when).days
        branches.append(
            {
                "name": name,
                "date": when,
                "age_days": age_days,
                "author": parts[2] if len(parts) > 2 else "",
                "subject": parts[3] if len(parts) > 3 else "",
            }
        )
    return branches


def delete_branch(name: str, remote: bool = False, force: bool = False, cwd: Optional[str] = None) -> bool:
    try:
        if remote:
            # name like origin/foo
            if "/" in name:
                remote_name, branch = name.split("/", 1)
                _run(["push", remote_name, "--delete", branch], cwd=cwd)
            else:
                _run(["branch", "-D" if force else "-d", name], cwd=cwd)
        else:
            flag = "-D" if force else "-d"
            _run(["branch", flag, name], cwd=cwd)
        return True
    except subprocess.CalledProcessError:
        return False