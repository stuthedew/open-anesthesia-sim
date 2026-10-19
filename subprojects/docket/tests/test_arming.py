"""Tests for what `bin/docket arm` prints, read from `arming.Verdict.lines`.

The branch-reading half of `arm` is tested through the command in
`test_cli.py`'s `test_arm_` tests. These pin the printed advice on its own,
and the hold on long simulator prose that no review has covered (`PL-W04Z`).
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pytest

from docket import arming, cli
from docket.claims import Hold
from docket.config import Config

SINCE = datetime(2026, 10, 18, 13, 0, tzinfo=UTC)


def test_a_hold_without_a_claim_says_a_repair_rides_the_owners_arm() -> None:
    """A held pull request the owner armed stays armed through a repair push (`PL-XTBF`).

    `docs/maintainer.md` tells the owner to leave auto-merge armed while a
    session fixes such a pull request. The hold line alone told the session to
    disarm it, which strands the fix green and unarmed.
    """
    verdict = arming.Verdict(answer=arming.HOLD, branch="claude/x", base="origin/main", gate=True)

    lines = verdict.lines

    disarm = next(i for i, line in enumerate(lines) if "Leave auto-merge off" in line)
    assert lines[disarm + 1] == arming.REPAIR_EXCEPTION
    assert "armed it after reading" in arming.REPAIR_EXCEPTION
    assert "docs/maintainer.md" in arming.REPAIR_EXCEPTION


def test_a_hold_by_a_claim_keeps_a_draft_and_names_no_repair() -> None:
    """A claim keeps the pull request a draft, which the owner never armed."""
    hold = Hold(
        key="PL-B7QX",
        ref="claude/x",
        kind="claim",
        state="live",
        since=SINCE,
        renewed=SINCE,
        commit="0123456789abcdef",
    )
    verdict = arming.Verdict(
        answer=arming.HOLD, branch="claude/x", base="origin/main", claims=(hold,)
    )

    lines = verdict.lines

    assert any("keep the pull request a draft" in line for line in lines)
    assert arming.REPAIR_EXCEPTION not in lines


def test_an_arm_answer_names_no_repair() -> None:
    verdict = arming.Verdict(answer=arming.ARM, branch="claude/x", base="origin/main")

    assert arming.REPAIR_EXCEPTION not in verdict.lines


# How `arm` holds a simulator change whose long prose has no recorded review
# (`PL-W04Z`). These call `arming.arm` with the count stubbed, because what
# `tools/new_prose.py --count` counts is pinned by its own tests.

SIMULATOR = "src/anesthesia_sim/core/uptake.py"
NOW = datetime(2026, 10, 19, 12, 0, tzinfo=UTC)


def _repo(tmp_path: Path) -> tuple[Path, Callable[..., str]]:
    """A clone of a bare `origin` whose `main` holds the store, checked out on a branch."""
    remote, root = tmp_path / "origin.git", tmp_path / "work"
    for target in (["--bare", str(remote)], [str(root)]):
        subprocess.run(
            ["git", "-c", "init.defaultBranch=main", "init", "-q", *target],
            check=True,
            capture_output=True,
        )

    def git(*args: str) -> str:
        done = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
        return done.stdout

    git("config", "user.email", "t@example.com")
    git("config", "user.name", "T")
    (root / "docs/items").mkdir(parents=True)
    (root / "docs/items/.keep").write_text("", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "base")
    git("remote", "add", "origin", str(remote))
    git("push", "-q", "-u", "origin", "main")
    git("checkout", "-qb", "claude/prose")
    return root, git


def _change(root: Path, git: Callable[..., str], path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", f"edit {path}")


def _record(git: Callable[..., str], *trailers: str) -> str:
    body = "\n".join(trailers)
    git("commit", "-q", "--allow-empty", "-m", f"record\n\n{body}")
    return git("rev-parse", "HEAD").strip()


def _arm(root: Path, count: Callable[[str], arming.ProseCount] | None) -> arming.Verdict:
    return arming.arm(root, items_dir="docs/items", now=NOW, fetch=False, prose_count=count)


NOT_NEEDED = "Owner-read: not needed - a refactor with its outputs pinned"


def test_arm_holds_without_prose_review(tmp_path: Path) -> None:
    """New long prose holds until a `Prose-review` record covers it, and again after a later one."""
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")
    _record(git, NOT_NEEDED)
    counts = {"": 1}
    asked: list[str] = []

    def count(since: str) -> arming.ProseCount:
        asked.append(since)
        return arming.ProseCount(count=counts[since])

    held = _arm(root, count)

    assert held.answer == arming.HOLD
    assert held.lines[0] == (
        "hold - claude/prose: it adds 1 long docstring or comment in the simulator since it "
        "forked, and no Prose-review record covers it"
    )
    assert arming.PROSE_ASK in held.lines
    assert asked == [""]

    review = _record(git, "Prose-review: read 1, rewrote 1, rejected 0")
    counts[review] = 0

    assert _arm(root, count).answer == arming.ARM
    assert asked[-1] == review

    _change(root, git, SIMULATOR, '"""A new long docstring."""\nX = 1\n')
    _record(git, NOT_NEEDED)
    counts[review] = 2

    again = _arm(root, count)

    assert again.answer == arming.HOLD
    assert again.lines[0].endswith(
        f"it adds 2 long docstrings and comments in the simulator since the Prose-review record "
        f"on {review[:12]}, and no Prose-review record covers them"
    )


def test_arm_holds_when_prose_count_fails(tmp_path: Path) -> None:
    """A count that could not be read holds, so unreadable prose is never armed as none."""
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")
    _record(git, NOT_NEEDED)

    def count(since: str) -> arming.ProseCount:
        return arming.ProseCount(declined="`new_prose --count` exited 2")

    held = _arm(root, count)

    assert held.answer == arming.HOLD
    assert held.lines[0] == (
        "hold - claude/prose: how many long docstrings and comments it adds since it forked "
        "could not be counted - `new_prose --count` exited 2"
    )
    assert arming.PROSE_UNCOUNTED in held.lines
    assert arming.PROSE_ASK not in held.lines


def test_one_hold_names_both_missing_records(tmp_path: Path) -> None:
    """With neither record, one answer asks for both, so one commit can carry both trailers."""
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")

    held = _arm(root, lambda since: arming.ProseCount(count=1))

    assert "no Owner-read record" in held.lines[0]
    assert "no Prose-review record covers it" in held.lines[0]
    assert arming.JUDGE_ASK in held.lines
    assert arming.PROSE_ASK in held.lines


def test_a_change_outside_the_simulator_asks_for_no_count(tmp_path: Path) -> None:
    root, git = _repo(tmp_path)
    _change(root, git, "tools/script.py", '"""A tool."""\n')

    def count(since: str) -> arming.ProseCount:
        raise AssertionError("the prose of a change outside the simulator was counted")

    assert _arm(root, count).answer == arming.ARM


def test_a_malformed_prose_record_is_said_and_covers_nothing(tmp_path: Path) -> None:
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")
    _record(git, NOT_NEEDED, "Prose-review: done")
    asked: list[str] = []

    def count(since: str) -> arming.ProseCount:
        asked.append(since)
        return arming.ProseCount(count=1)

    held = _arm(root, count)

    assert held.answer == arming.HOLD
    assert asked == [""]
    assert any("is not 'read N, rewrote M, rejected K'" in line for line in held.lines)


@pytest.mark.parametrize(
    ("script", "expected"),
    [
        ("print(3)", arming.ProseCount(count=3)),
        ("print('three')", None),
        ("import sys; sys.exit(2)", None),
    ],
)
def test_the_prose_count_command_is_read_as_one_whole_number(
    tmp_path: Path, script: str, expected: arming.ProseCount | None
) -> None:
    """`prose_count_command` is handed the record's commit, and only a whole number is a count."""
    program = tmp_path / "count.py"
    program.write_text(
        f"import sys\nopen(sys.argv[0] + '.args', 'w').write(' '.join(sys.argv[1:]))\n{script}\n"
    )
    ask = cli._prose_count(tmp_path, Config(prose_count_command=f"{sys.executable} {program}"))
    assert ask is not None

    answered = ask("abc123")

    assert (tmp_path / "count.py.args").read_text() == "abc123"
    if expected is None:
        assert answered.count == 0
        assert answered.declined
    else:
        assert answered == expected
