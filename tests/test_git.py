import subprocess
import tempfile
import os
from datetime import datetime, timezone, timedelta

from branch_age.git import list_branches, is_repo, current_branch


def make_repo():
    d = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=d, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=d, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=d, check=True)
    # initial commit
    p = os.path.join(d, "f.txt")
    with open(p, "w") as f:
        f.write("hi")
    subprocess.run(["git", "add", "f.txt"], cwd=d, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=d, check=True)
    return d


def test_is_repo():
    d = make_repo()
    assert is_repo(d) is True
    assert is_repo(tempfile.mkdtemp()) is False


def test_current_branch():
    d = make_repo()
    assert current_branch(d) == "main"


def test_list_branches():
    d = make_repo()
    # create an old branch by committing with a past date
    subprocess.run(["git", "checkout", "-q", "-b", "old"], cwd=d, check=True)
    with open(os.path.join(d, "g.txt"), "w") as f:
        f.write("x")
    env = dict(os.environ, GIT_AUTHOR_DATE="2020-01-01T00:00:00", GIT_COMMITTER_DATE="2020-01-01T00:00:00")
    subprocess.run(["git", "add", "g.txt"], cwd=d, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "old commit"], cwd=d, env=env, check=True)
    subprocess.run(["git", "checkout", "-q", "main"], cwd=d, check=True)

    branches = list_branches(cwd=d)
    names = [b["name"] for b in branches]
    assert "main" in names
    assert "old" in names
    old = next(b for b in branches if b["name"] == "old")
    assert old["age_days"] > 1000