"""Tests for `.claude/hooks/docket-digest.sh`, the session-start digest.

Only the branch-position half is exercised here. The digest itself is
`bin/docket digest`, tested with the rest of that package.

What this file held was the part written in shell, which nothing else could
reach. That part is now `bin/docket branch`, and these run the hook end to end
against the real command instead - the fixtures install a shim that execs this
repository's own `bin/docket`, so what is under test is the whole path a
session start takes: hook, fetch, command, git.

The fixtures are real git repositories - a bare remote, a shallow clone of it,
and a remote that has since moved - because the behaviour under test is git's
own answer to a question about a clone's shape, and a stub would test the
stub. They are local `file://` remotes, so nothing here touches a network.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "docket-digest.sh"


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

    _install_docket(work)
    return work


def _install_docket(root: Path) -> None:
    """The store the hook requires, and a `bin/docket` that is the real one.

    A shim rather than a copy: `bin/docket` resolves the package from its own
    location, so execing this repository's copy is what makes the command under
    test the command that ships. The store is left empty - `digest` then prints
    nothing, and these tests are about the branch line.
    """
    (root / "docs" / "items").mkdir(parents=True)
    shim = root / "bin" / "docket"
    shim.parent.mkdir()
    shim.write_text(f'#!/bin/sh\nexec "{REPO / "bin" / "docket"}" "$@"\n', encoding="utf-8")
    shim.chmod(0o755)


def _break_the_remote(root: Path) -> None:
    """Point `origin` at nothing, so every fetch fails the way no network does.

    The deepening PL-K2ZK added is allowed to fail, and what it must not do is
    fail loudly or hold the session open. A path that does not exist fails
    immediately and locally, which is the offline case without the wait.
    """
    _git("remote", "set-url", "origin", str(root / "no-such-remote.git"), cwd=root)


def _is_shallow(root: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip() == "true"


def _run_hook(root: Path) -> str:
    """The hook as a session start runs it: from the project directory.

    `cwd` is load-bearing rather than tidiness - `docket` resolves the store
    from the working directory, so a hook run from somewhere else would answer
    confidently about the wrong repository.
    """
    result = subprocess.run(
        ["bash", str(HOOK)],
        cwd=root,
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


def test_a_shallow_checkout_is_deepened_once_at_session_start(tmp_path: Path) -> None:
    """PL-K2ZK: the hook repairs the truncation instead of reading around it.

    The container's clone is shallow, so `branches_in_flight` cannot find a
    merge base and declines - in every session, for the life of the container.
    One fetch converts that non-answer into the right answer, so the hook takes
    it before anything below reads a ref.
    """
    work = _shallow_clone_of_a_moved_remote(tmp_path)
    assert _is_shallow(work)

    out = _run_hook(work)

    assert not _is_shallow(work)
    assert "is 2 behind origin/main with nothing of its own" in out


def test_a_clone_sharing_no_history_is_repaired_rather_than_reported(tmp_path: Path) -> None:
    """PL-FBCC's state is now reachable only when the deepening cannot run.

    `rev-list A...B` answers an unrelated pair without failing - it prints the
    size of each side, which reads exactly like a real position, and a
    fabricated "ahead" tells a session it carries work it does not. A `--depth`
    fetch re-truncates `origin/main` and records it in `.git/shallow`, which no
    later *ordinary* fetch undoes. The deepening is not an ordinary fetch, so
    with a reachable remote the session now gets the number rather than the
    complaint.
    """
    work = _shallow_clone_of_a_moved_remote(tmp_path)
    _git("fetch", "--quiet", "--depth=1", "origin", "+refs/heads/*:refs/remotes/origin/*", cwd=work)

    out = _run_hook(work)

    assert "is 2 behind origin/main with nothing of its own" in out
    assert "shares no readable history with origin/main" not in out


def test_an_unreachable_remote_leaves_the_complaint_and_starts_cleanly(tmp_path: Path) -> None:
    """The offline half of PL-K2ZK: silence from the fetch, not from the hook.

    A container with no network must still start, and must still be told what
    its history cannot answer. So the deepening fails quietly, the checkout is
    left exactly as truncated as it was, and the guard PL-MGNC put in is what
    speaks - including the remedy a person can run once they have a network.
    """
    work = _shallow_clone_of_a_moved_remote(tmp_path)
    _git("fetch", "--quiet", "--depth=1", "origin", "+refs/heads/*:refs/remotes/origin/*", cwd=work)
    _break_the_remote(work)

    out = _run_hook(work)

    assert _is_shallow(work)
    assert "shares no readable history with origin/main" in out
    assert "git fetch --deepen=100 origin" in out
    assert "ahead" not in out


def test_the_repair_the_hook_names_actually_repairs_it(tmp_path: Path) -> None:
    """A remedy printed to a session is worth nothing unless it has been run.

    Run with the remote broken afterwards, so what the position line proves is
    the hand-run `--deepen`, not the hook deepening it a second time.
    """
    work = _shallow_clone_of_a_moved_remote(tmp_path)
    _git("fetch", "--quiet", "--depth=1", "origin", "+refs/heads/*:refs/remotes/origin/*", cwd=work)

    _git("fetch", "--quiet", "--deepen=100", "origin", cwd=work)
    _break_the_remote(work)

    assert "is 2 behind origin/main with nothing of its own" in _run_hook(work)


def test_a_repository_with_no_remote_branch_says_nothing(tmp_path: Path) -> None:
    """Silence, not a shallow-clone complaint: there is nothing to compare to.

    The comparison would be the default branch against itself, which answers
    nothing, and this text is resent on every turn of the session. `docket
    branch` says why when a person asks it directly; `--brief` is what the hook
    passes, and it keeps the silence.
    """
    root = tmp_path / "solo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git("config", name, value, cwd=root)
    _install_docket(root)
    (root / "f.txt").write_text("x", encoding="utf-8")
    _git("add", "-A", cwd=root)
    _git("commit", "-qm", "only", cwd=root)

    assert "Branch:" not in _run_hook(root)
