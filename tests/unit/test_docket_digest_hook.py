"""Tests for `.claude/hooks/docket-digest.sh`, the session-start digest.

Only the branch-position half is exercised here. The digest itself is
`bin/docket digest`, tested with the rest of that package; what this file
holds is the part written in shell, which nothing else can reach.

The fixtures are real git repositories - a bare remote, a shallow clone of
it, and a remote that has since moved - because the behaviour under test is
git's own answer to a question about a clone's shape, and a stub would test
the stub. They are local `file://` remotes, so nothing here touches a network.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "docket-digest.sh"


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _shallow_clone_of_a_moved_remote(tmp_path: Path) -> Path:
    """A depth-3 clone, on a feature branch, whose remote has gained two commits.

    This is the shape a session container is in: shallow, working a branch the
    harness named, and behind whatever has landed since the clone was made.
    """
    remote = tmp_path / "remote.git"
    seed = tmp_path / "seed"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git("config", name, value, cwd=seed)
    for index in range(6):
        (seed / "f.txt").write_text(str(index), encoding="utf-8")
        _git("add", "-A", cwd=seed)
        _git("commit", "-qm", f"c{index}", cwd=seed)
    _git("push", "-q", str(remote), "main", cwd=seed)
    subprocess.run(["git", "clone", "-q", "--depth=3", f"file://{remote}", str(work)], check=True)
    _git("checkout", "-qb", "claude/topic", cwd=work)
    for index in range(6, 8):
        (seed / "f.txt").write_text(str(index), encoding="utf-8")
        _git("add", "-A", cwd=seed)
        _git("commit", "-qm", f"c{index}", cwd=seed)
    _git("push", "-q", str(remote), "main", cwd=seed)

    # The hook declines unless the store and the command it runs are both
    # present, and neither is what these tests are about.
    (work / "docs" / "items").mkdir(parents=True)
    stub = work / "bin" / "docket"
    stub.parent.mkdir()
    stub.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    stub.chmod(0o755)
    return work


def _run_hook(root: Path) -> str:
    result = subprocess.run(
        ["bash", str(HOOK)],
        env={
            "CLAUDE_PROJECT_DIR": str(root),
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            "HOME": str(root),
        },
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout


def test_a_shallow_clone_behind_its_remote_is_counted_correctly(tmp_path: Path) -> None:
    """The ordinary container: shallow, and behind what has landed since."""
    work = _shallow_clone_of_a_moved_remote(tmp_path)

    out = _run_hook(work)

    assert "is 2 behind origin/main with nothing of its own" in out


def test_a_clone_sharing_no_history_says_so_instead_of_counting(tmp_path: Path) -> None:
    """PL-FBCC: `rev-list A...B` answers an unrelated pair without failing.

    It prints the size of each side, which reads exactly like a real position -
    and a fabricated "ahead" tells a session it carries work it does not,
    arguing against the merge this line exists to prompt.
    """
    work = _shallow_clone_of_a_moved_remote(tmp_path)
    # A `--depth` fetch re-truncates `origin/main` and records it in
    # `.git/shallow`, which no later ordinary fetch undoes.
    _git("fetch", "--quiet", "--depth=1", "origin", "+refs/heads/*:refs/remotes/origin/*", cwd=work)

    out = _run_hook(work)

    assert "shares no readable history with origin/main" in out
    assert "git fetch --deepen=100 origin" in out
    assert "ahead" not in out


def test_the_repair_the_hook_names_actually_repairs_it(tmp_path: Path) -> None:
    """A remedy printed to a session is worth nothing unless it has been run."""
    work = _shallow_clone_of_a_moved_remote(tmp_path)
    _git("fetch", "--quiet", "--depth=1", "origin", "+refs/heads/*:refs/remotes/origin/*", cwd=work)

    _git("fetch", "--quiet", "--deepen=100", "origin", cwd=work)

    assert "is 2 behind origin/main with nothing of its own" in _run_hook(work)


def test_a_repository_with_no_remote_branch_says_nothing(tmp_path: Path) -> None:
    """Silence, not a shallow-clone complaint: there is nothing to compare to."""
    root = tmp_path / "solo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git("config", name, value, cwd=root)
    (root / "docs" / "items").mkdir(parents=True)
    stub = root / "bin" / "docket"
    stub.parent.mkdir()
    stub.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    stub.chmod(0o755)
    (root / "f.txt").write_text("x", encoding="utf-8")
    _git("add", "-A", cwd=root)
    _git("commit", "-qm", "only", cwd=root)

    assert "Branch:" not in _run_hook(root)
