"""Tests for `.claude/hooks/docket-branch-guard.sh`, the first-edit branch check.

`PL-1CYR` made the branch's position askable at any moment; this hook is what
asks it, at the moment a discussion becomes implementation. What has to hold is
narrow and easy to get silently wrong, which is why each of these exists: the
line has to travel in the JSON form a session can actually read, the hook must
not grant the permission it is attached to, it must ask once per session rather
than once per edit, and it must say nothing when there is nothing to say. The
claim question (`PL-J9S0`) adds the same three at a different moment: the
first edit that is work, which a capture's edit is not.

Real git and a local `file://` remote, so nothing here touches a network.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "docket-branch-guard.sh"


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _clone_of_a_moved_remote(
    tmp_path: Path, *, moved: bool = True, branch: str = "claude/pl-k7qx-live"
) -> Path:
    """A checkout on its own branch, with the remote's `main` ahead of it or not.

    The session the check exists for: opened to discuss the next piece of work,
    sitting while another session merges.
    """
    remote = tmp_path / "remote.git"
    seed = tmp_path / "seed"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git("config", name, value, cwd=seed)
    (seed / "f.txt").write_text("0", encoding="utf-8")
    _git("add", "-A", cwd=seed)
    _git("commit", "-qm", "c0", cwd=seed)
    _git("push", "-q", str(remote), "main", cwd=seed)
    subprocess.run(["git", "clone", "-q", f"file://{remote}", str(work)], check=True)
    _git("checkout", "-qb", branch, cwd=work)

    if moved:
        (seed / "f.txt").write_text("1", encoding="utf-8")
        _git("add", "-A", cwd=seed)
        _git("commit", "-qm", "PL-9Y42 Validate wash-in (#131)", cwd=seed)
        _git("push", "-q", str(remote), "main", cwd=seed)

    (work / "docs" / "items").mkdir(parents=True)
    shim = work / "bin" / "docket"
    shim.parent.mkdir()
    shim.write_text(f'#!/bin/sh\nexec "{REPO / "bin" / "docket"}" "$@"\n', encoding="utf-8")
    shim.chmod(0o755)
    # `bin/docket` execs bare `python3`, and `_guard_env` leads `PATH` with this
    # `bin/`, so the hook runs under the interpreter running this suite rather
    # than the machine's own - Apple's 3.9 on macOS, below docket's 3.11 floor,
    # which failed three tests here on the project owner's Mac while CI stayed
    # green (`PL-Y6W9`). `test_docket_digest_hook.py` carries the full account.
    (work / "bin" / "python3").symlink_to(sys.executable)
    return work


def _guard_env(root: Path, tmp_path: Path) -> dict[str, str]:
    """The environment the hook runs under, fixed so nothing leaks in from pytest's."""
    return {
        "CLAUDE_PROJECT_DIR": str(root),
        "PATH": f"{root / 'bin'}:/usr/bin:/bin:/usr/local/bin",
        "HOME": str(root),
        "TMPDIR": str(tmp_path / "markers"),
        # For the checkout's copy of `tools/branch_id_check.py`, which finds
        # `docket` beside itself, where this checkout carries none.
        "PYTHONPATH": str(REPO / "subprojects" / "docket" / "src"),
    }


def _run_guard(
    root: Path, tmp_path: Path, session: str = "s1", target: Path | None = None
) -> subprocess.CompletedProcess[str]:
    payload: dict[str, object] = {"session_id": session, "tool_name": "Edit", "cwd": str(root)}
    if target is not None:
        payload["tool_input"] = {"file_path": str(target)}
    return subprocess.run(
        ["bash", str(HOOK)],
        cwd=root,
        input=json.dumps(payload),
        env=_guard_env(root, tmp_path),
        capture_output=True,
        text=True,
        check=False,
    )


def test_branch_guard_speaks_before_the_first_edit_when_the_base_has_moved(tmp_path: Path) -> None:
    """The line has to reach the session, which plain stdout does not do.

    A `PreToolUse` hook's stdout goes to the debug log; only the JSON form's
    `additionalContext` is read into context. A hook that echoed the line would
    look right in a terminal and be invisible where it matters.
    """
    (tmp_path / "markers").mkdir()
    work = _clone_of_a_moved_remote(tmp_path)

    result = _run_guard(work, tmp_path)

    assert result.returncode == 0
    payload = json.loads(result.stdout)["hookSpecificOutput"]
    assert payload["hookEventName"] == "PreToolUse"
    assert "behind origin/main" in payload["additionalContext"]
    assert "PL-9Y42" in payload["additionalContext"]


def test_branch_guard_does_not_grant_the_permission_it_is_attached_to(tmp_path: Path) -> None:
    """`permissionDecision: allow` would auto-approve the edit that triggered it.

    The hook exists to say something, never to grant something, and the two
    live one key apart in the same object.
    """
    (tmp_path / "markers").mkdir()
    work = _clone_of_a_moved_remote(tmp_path)

    payload = json.loads(_run_guard(work, tmp_path).stdout)

    assert "permissionDecision" not in payload["hookSpecificOutput"]


def test_branch_guard_asks_once_per_session_not_once_per_edit(tmp_path: Path) -> None:
    """It fetches, so per-edit would be a worse tax than the conflict it prevents."""
    (tmp_path / "markers").mkdir()
    work = _clone_of_a_moved_remote(tmp_path)

    first = _run_guard(work, tmp_path)
    second = _run_guard(work, tmp_path)
    other_session = _run_guard(work, tmp_path, session="s2")

    assert first.stdout
    assert second.stdout == ""
    assert other_session.stdout, "a different session gets its own answer"


def test_branch_guard_says_nothing_when_the_base_has_not_moved(tmp_path: Path) -> None:
    """A hook that speaks unasked earns each line, and this one has none to say."""
    (tmp_path / "markers").mkdir()
    work = _clone_of_a_moved_remote(tmp_path, moved=False)

    result = _run_guard(work, tmp_path)

    assert result.returncode == 0
    assert result.stdout == ""


def test_branch_guard_lets_the_edit_through_when_it_cannot_run(tmp_path: Path) -> None:
    """Every failure is the session's to ignore: it edits normally regardless."""
    (tmp_path / "markers").mkdir()
    result = subprocess.run(
        ["bash", str(HOOK)],
        input='{"session_id": "s3"}',
        env={"PATH": "/usr/bin:/bin:/usr/local/bin", "TMPDIR": str(tmp_path / "markers")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == ""


def test_the_hook_runs_under_the_interpreter_running_this_suite(tmp_path: Path) -> None:
    """`bin/docket` execs bare `python3`, and the fixture decides which one that is.

    An identity rather than a floor, for the reason `test_docket_digest_hook.py`
    gives: a floor fails only where the project owner is standing, and this
    fails anywhere the fixture goes back to the system directories.
    """
    (tmp_path / "markers").mkdir()
    work = _clone_of_a_moved_remote(tmp_path, moved=False)

    found = subprocess.run(
        ["bash", "-c", "python3 -c 'import sys; print(sys.version)'"],
        env=_guard_env(work, tmp_path),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    assert found == sys.version, f"the hook gets {found}, not this suite's {sys.version}"


def _with_the_check(work: Path) -> None:
    """The checkout's own `tools/branch_id_check.py`, which the claim question asks.

    Copied rather than linked: the check finds its repository from its own
    path, and a link would resolve to this one.
    """
    (work / "tools").mkdir()
    shutil.copy(REPO / "tools" / "branch_id_check.py", work / "tools" / "branch_id_check.py")


def test_branch_guard_says_to_claim_before_the_first_edit_that_is_work(tmp_path: Path) -> None:
    """A fresh session's branch claims nothing, and the first edit of work hears so, once."""
    (tmp_path / "markers").mkdir()
    work = _clone_of_a_moved_remote(tmp_path, moved=False, branch="claude/some-session-a1b2c3")
    _with_the_check(work)

    first = _run_guard(work, tmp_path, target=work / "src" / "work.py")
    again = _run_guard(work, tmp_path, target=work / "src" / "work.py")

    context = json.loads(first.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "this branch claims nothing: `bin/docket claim <id>`" in context
    assert again.stdout == ""


def test_branch_guard_keeps_the_claim_question_past_a_capture(tmp_path: Path) -> None:
    """An item file is not work: asking there would spend the question on nothing."""
    (tmp_path / "markers").mkdir()
    work = _clone_of_a_moved_remote(tmp_path, moved=False, branch="claude/some-session-a1b2c3")
    _with_the_check(work)

    capture = _run_guard(work, tmp_path, target=work / "docs" / "items" / "PL-K7QX-x.md")
    later = _run_guard(work, tmp_path, target=work / "src" / "work.py")

    assert capture.stdout == ""
    assert "this branch claims nothing" in later.stdout
