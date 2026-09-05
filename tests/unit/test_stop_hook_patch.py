"""Tests for `.claude/hooks/stop_hook_patch.py`, the SessionStart correction to the
harness stop hook.

The tool edits a file it does not own, which every `Stop` in the session then
executes, so the failure worth guarding is not "the patch did not apply" but
"the patch applied to something it should not have". Hence the tests for an
absent line and for a second occurrence, and the assertion that exactly one
line of the script moves: a hook that no longer parses would break the session
it was written to help.

`test_the_correction_is_what_git_actually_answers` is the one that proves the
*claim* rather than the edit. Everything else here would pass just as happily
if `HEAD --not --remotes` were the wrong incantation, so that test builds a
real repository in the shape `PL-WW08` describes - a merged branch's tracking
ref left behind, pointing at a commit `main` has moved past - and asserts the
two forms disagree exactly there, and agree where work is genuinely unpushed.
It needs no copy of the harness script, so it cannot rot with one.
"""

from __future__ import annotations

import shutil
import stat
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
import stop_hook_patch

#: The tail of `~/.claude/stop-hook-git-check.sh` as the harness ships it,
#: transcribed verbatim on 2026-09-04. Written out here rather than built from
#: the tool's own constants, so a typo in `VULNERABLE` fails a test instead of
#: matching itself.
SHIPPED = """\
#!/bin/bash

current_branch=$(git branch --show-current)
if [[ -n "$current_branch" ]]; then
  if git rev-parse "origin/$current_branch" >/dev/null 2>&1; then
    upstream="origin/$current_branch"
  else
    upstream="origin/HEAD"
  fi

  unpushed=$(git rev-list "$upstream..HEAD" --count 2>/dev/null) || unpushed=0
  if [[ "$unpushed" -gt 0 ]]; then
    if [[ "$upstream" == "origin/$current_branch" ]]; then
      echo "There are $unpushed unpushed commit(s) on branch '$current_branch'." >&2
    else
      echo "Branch '$current_branch' has $unpushed unpushed commit(s)." >&2
    fi
    exit 2
  fi
fi

exit 0
"""


def _hook(tmp_path: Path, source: str = SHIPPED) -> Path:
    path = tmp_path / "stop-hook-git-check.sh"
    path.write_text(source, encoding="utf-8")
    path.chmod(0o755)
    return path


def _run(path: Path) -> int:
    return stop_hook_patch.main(["stop_hook_patch.py", str(path)])


def _git(root: Path) -> Callable[..., str]:
    def run(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
        ).stdout

    return run


def _commit(run: Callable[..., str], root: Path, message: str) -> str:
    (root / "file.txt").write_text(message, encoding="utf-8")
    run("add", "file.txt")
    run("commit", "-m", message)
    return run("rev-parse", "HEAD").strip()


def test_the_shipped_line_is_corrected_and_nothing_else_moves(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The whole edit, and its blast radius: one line."""
    path = _hook(tmp_path)

    assert _run(path) == 0

    before = SHIPPED.splitlines()
    after = path.read_text(encoding="utf-8").splitlines()
    assert len(after) == len(before)
    moved = [index for index, (a, b) in enumerate(zip(before, after, strict=True)) if a != b]
    assert len(moved) == 1
    assert after[moved[0]] == stop_hook_patch.CORRECTED.rstrip("\n")
    # The `$upstream` the message below the count still reads is untouched.
    assert '"$upstream" == "origin/$current_branch"' in "\n".join(after)
    assert capsys.readouterr().out == ""


def test_running_twice_leaves_the_file_untouched_and_silent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every session runs this against a file some session may already have
    corrected, so a second run has to be a no-op rather than a report."""
    path = _hook(tmp_path)
    _run(path)
    once = path.read_text(encoding="utf-8")
    capsys.readouterr()

    assert _run(path) == 0
    assert path.read_text(encoding="utf-8") == once
    assert capsys.readouterr().out == ""


def test_a_hook_that_changed_upstream_is_left_alone_and_reported(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The case the tool exists to survive: the hook is rewritten upstream, the
    line is no longer there, and the session is told - because the false demand
    is live again and disproving one is back to being manual."""
    source = SHIPPED.replace(
        stop_hook_patch.VULNERABLE, "  unpushed=$(some_new_thing) || unpushed=0\n"
    )
    path = _hook(tmp_path, source)

    assert _run(path) == 0
    assert path.read_text(encoding="utf-8") == source
    report = capsys.readouterr().out
    assert "the line it rewrites is not there" in report
    assert "git ls-remote --heads origin" in report
    assert "--prune" in report


def test_a_second_occurrence_is_left_alone_rather_than_guessed_at(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Two matches means this is not the script the tool was written against,
    and rewriting the wrong one silently breaks every stop in the session."""
    source = SHIPPED + stop_hook_patch.VULNERABLE
    path = _hook(tmp_path, source)

    assert _run(path) == 0
    assert path.read_text(encoding="utf-8") == source
    assert "the line it rewrites is not there" in capsys.readouterr().out


def test_a_missing_hook_is_silent(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The ordinary case away from the harness - a local checkout with no
    `~/.claude/stop-hook-git-check.sh`. Reporting it would put a line in every
    such session's context to say that nothing is wrong."""
    assert _run(tmp_path / "absent.sh") == 0
    assert capsys.readouterr().out == ""


def test_the_executable_bit_survives(tmp_path: Path) -> None:
    """The file is a hook command: a rewrite that dropped its mode would leave
    every stop in the session failing to execute it."""
    path = _hook(tmp_path)
    _run(path)
    assert stat.S_IMODE(path.stat().st_mode) == 0o755


def test_a_failed_write_is_reported_and_leaves_nothing_behind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A read-only home must not fail the session, must not truncate the hook,
    and must not strand the scratch file beside it.

    The write is made to fail rather than the directory made read-only: this
    suite runs as root in a container, where mode bits are not enforced.
    """
    path = _hook(tmp_path)

    def refuse(*args: object, **kwargs: object) -> tuple[int, str]:
        raise OSError("read-only file system")

    monkeypatch.setattr(stop_hook_patch.tempfile, "mkstemp", refuse)

    assert _run(path) == 0
    assert path.read_text(encoding="utf-8") == SHIPPED
    assert list(tmp_path.iterdir()) == [path]
    assert "writing it failed" in capsys.readouterr().out


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash is not installed")
def test_the_corrected_script_still_parses_as_bash(tmp_path: Path) -> None:
    """`bash -n` on the result, because the tool's output is executed rather
    than read: a quoting mistake in the replacement would surface as every stop
    in the session failing, not as a test."""
    path = _hook(tmp_path)
    _run(path)
    assert subprocess.run(["bash", "-n", str(path)], check=False).returncode == 0


def test_the_correction_is_what_git_actually_answers(tmp_path: Path) -> None:
    """The claim under the edit, against a real repository.

    Built in the shape `PL-WW08` describes: a branch was merged, so its remote
    head is gone but its tracking ref survives at the commit it was cut from,
    and `main` has moved on. The shipped form counts everything `main` gained
    as unpushed; the correction counts nothing, because those commits sit on
    `refs/remotes/origin/main`. Then a genuinely unpushed commit, where the two
    have to agree - a correction that simply stopped counting would pass every
    assertion above and silence a demand that was true.
    """
    run = _git(tmp_path)
    run("init", "--initial-branch=main")
    run("config", "user.email", "test@example.com")
    run("config", "user.name", "Test")
    run("config", "commit.gpgsign", "false")
    first = _commit(run, tmp_path, "first")
    run("update-ref", "refs/remotes/origin/main", first)
    # The branch as it stood when its pull request was open.
    run("update-ref", "refs/remotes/origin/feature", first)
    second = _commit(run, tmp_path, "second")
    third = _commit(run, tmp_path, "third")
    run("update-ref", "refs/remotes/origin/main", third)
    # The merge deleted the remote branch and left the tracking ref behind.
    # `CLAUDE.md` restarts such a branch from the default branch.
    run("checkout", "-B", "feature", third)

    shipped = run("rev-list", "origin/feature..HEAD", "--count").strip()
    corrected = run("rev-list", "HEAD", "--not", "--remotes", "--count").strip()
    assert (shipped, corrected) == ("2", "0"), (
        "the stale ref should make the shipped test demand a push for "
        f"{second[:7]} and {third[:7]}, and the correction should not"
    )

    _commit(run, tmp_path, "genuinely unpushed")
    assert run("rev-list", "HEAD", "--not", "--remotes", "--count").strip() == "1"
