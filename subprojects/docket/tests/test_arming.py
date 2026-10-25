"""Tests for what `bin/docket arm` prints, read from `arming.Verdict.lines`.

The branch-reading half of `arm` is tested through the command in
`test_cli.py`'s `test_arm_` tests. These pin the printed advice on its own,
the hold on long simulator prose that no review has covered (`PL-W04Z`), and
the hold on blind review passes that no record says ran (`PL-HDRN`).
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


def _arm(
    root: Path,
    count: Callable[[str], arming.CommandCount] | None,
    blind: Callable[[], arming.CommandCount] | None = None,
) -> arming.Verdict:
    return arming.arm(
        root, items_dir="docs/items", now=NOW, fetch=False, prose_count=count, blind_count=blind
    )


NOT_NEEDED = "Owner-read: not needed - a refactor with its outputs pinned"


def test_arm_holds_without_prose_review(tmp_path: Path) -> None:
    """New long prose holds until a `Prose-review` record covers it, and again after a later one."""
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")
    _record(git, NOT_NEEDED)
    counts = {"": 1}
    asked: list[str] = []

    def count(since: str) -> arming.CommandCount:
        asked.append(since)
        return arming.CommandCount(count=counts[since])

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

    def count(since: str) -> arming.CommandCount:
        return arming.CommandCount(declined="`new_prose --count` exited 2")

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

    held = _arm(root, lambda since: arming.CommandCount(count=1))

    assert "no Owner-read record" in held.lines[0]
    assert "no Prose-review record covers it" in held.lines[0]
    assert arming.JUDGE_ASK in held.lines
    assert arming.PROSE_ASK in held.lines


def test_a_change_outside_the_simulator_asks_for_no_count(tmp_path: Path) -> None:
    root, git = _repo(tmp_path)
    _change(root, git, "tools/script.py", '"""A tool."""\n')

    def count(since: str) -> arming.CommandCount:
        raise AssertionError("the prose of a change outside the simulator was counted")

    assert _arm(root, count).answer == arming.ARM


def test_a_malformed_prose_record_is_said_and_covers_nothing(tmp_path: Path) -> None:
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")
    _record(git, NOT_NEEDED, "Prose-review: done")
    asked: list[str] = []

    def count(since: str) -> arming.CommandCount:
        asked.append(since)
        return arming.CommandCount(count=1)

    held = _arm(root, count)

    assert held.answer == arming.HOLD
    assert asked == [""]
    assert any("is not 'read N, rewrote M, rejected K'" in line for line in held.lines)


@pytest.mark.parametrize(
    ("script", "expected"),
    [
        ("print(3)", arming.CommandCount(count=3)),
        ("print('three')", None),
        ("import sys; sys.exit(2)", None),
    ],
)
def test_the_prose_count_command_is_read_as_one_whole_number(
    tmp_path: Path, script: str, expected: arming.CommandCount | None
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


# How `arm` holds a simulator change whose blind generalist review passes have
# no record (`PL-HDRN`). The count is stubbed, because what
# `tools/blind_review.py --count` counts is pinned by its own tests.

PASSES_TWO = "Blind-review: passes 2, findings 3, fixed 1, filed 1, rejected 1"


def test_arm_holds_without_blind_review(tmp_path: Path) -> None:
    """Missing passes hold, a record of too few still holds, and enough passes arm.

    A fix made after the passes leaves the record standing, because close-out
    step 9 says a fix made for a finding needs no further pass.
    """
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")
    _record(git, NOT_NEEDED)
    owed = arming.CommandCount(count=2)

    held = _arm(root, None, lambda: owed)

    assert held.answer == arming.HOLD
    assert held.lines[0] == (
        "hold - claude/prose: it owes 2 blind review passes, and no Blind-review record says "
        "any ran"
    )
    assert arming.BLIND_ASK in held.lines

    short = _record(git, "Blind-review: passes 1, findings 0, fixed 0, filed 0, rejected 0")

    again = _arm(root, None, lambda: owed)

    assert again.answer == arming.HOLD
    assert again.lines[0].endswith(
        f"it owes 2 blind review passes, and the Blind-review record on {short[:12]} records 1"
    )

    _record(git, PASSES_TWO)

    assert _arm(root, None, lambda: owed).answer == arming.ARM

    _change(root, git, SIMULATOR, "X = 2\n")
    _record(git, NOT_NEEDED)

    assert _arm(root, None, lambda: owed).answer == arming.ARM


def test_arm_holds_again_when_the_passes_owed_rise(tmp_path: Path) -> None:
    """A record of one pass no longer covers a branch that later owes two."""
    root, git = _repo(tmp_path)
    _change(root, git, "src/anesthesia_sim/app/panel.py", "X = 1\n")
    _record(git, NOT_NEEDED, "Blind-review: passes 1, findings 0, fixed 0, filed 0, rejected 0")

    assert _arm(root, None, lambda: arming.CommandCount(count=1)).answer == arming.ARM

    held = _arm(root, None, lambda: arming.CommandCount(count=2))

    assert held.answer == arming.HOLD
    assert "it owes 2 blind review passes" in held.lines[0]


def test_arm_holds_when_blind_count_fails(tmp_path: Path) -> None:
    """A count that could not be read holds, so a branch is never armed as owing no pass."""
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")
    _record(git, NOT_NEEDED, PASSES_TWO)

    held = _arm(root, None, lambda: arming.CommandCount(declined="`blind_review --count` exited 1"))

    assert held.answer == arming.HOLD
    assert held.lines[0] == (
        "hold - claude/prose: how many blind review passes it owes could not be counted - "
        "`blind_review --count` exited 1"
    )
    assert arming.BLIND_UNCOUNTED in held.lines
    assert arming.BLIND_ASK not in held.lines


def test_a_malformed_blind_record_is_said_and_covers_nothing(tmp_path: Path) -> None:
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")
    _record(git, NOT_NEEDED, "Blind-review: passes 2")

    held = _arm(root, None, lambda: arming.CommandCount(count=2))

    assert held.answer == arming.HOLD
    assert "no Blind-review record says any ran" in held.lines[0]
    assert any("is not 'passes N, findings F, fixed X, filed Y" in line for line in held.lines)


def test_a_change_outside_the_simulator_asks_for_no_blind_count(tmp_path: Path) -> None:
    root, git = _repo(tmp_path)
    _change(root, git, "tools/script.py", "X = 1\n")

    def blind() -> arming.CommandCount:
        raise AssertionError("the passes of a change outside the simulator were counted")

    assert _arm(root, None, blind).answer == arming.ARM


def test_the_blind_count_command_is_handed_nothing(tmp_path: Path) -> None:
    """`blind_count_command` is run as configured, and its whole number is the count."""
    program = tmp_path / "count.py"
    program.write_text(
        "import sys\nopen(sys.argv[0] + '.args', 'w').write(' '.join(sys.argv[1:]))\nprint(2)\n"
    )
    ask = cli._blind_count(tmp_path, Config(blind_count_command=f"{sys.executable} {program}"))
    assert ask is not None

    assert ask() == arming.CommandCount(count=2)
    assert (tmp_path / "count.py.args").read_text() == ""
    assert cli._blind_count(tmp_path, Config()) is None


@pytest.mark.parametrize(
    "value",
    [
        "Which view opens first? | Chooser: the learner picks a view each run | Last used: it "
        "opens where they left off | recommend Chooser - it names every view",
        "Which run opens? | A: the newest | B: the oldest | C: the pinned one | recommend C - it "
        "is the one the case names.",
        "risk - a dose label could read mg for mcg | checked - the formatter tests pin the unit. "
        "| look - the infusion panel's label",
    ],
)
def test_renders_owner_ask_recognizes_every_line_parse_owner_ask_renders(value: str) -> None:
    """The coordinator's guard reads the form through this, not through a copy (`PL-YV90`).

    A line inside a longer message is recognized too, since a post forwards it.
    """
    line, why = arming.parse_owner_ask(value)
    assert line, why

    assert arming.renders_owner_ask(line)
    assert arming.renders_owner_ask(f"The thread on #1700 asks: {line} Reply Merge it.")


@pytest.mark.parametrize(
    "text",
    [
        "Read #1700 and merge it.",
        # One option only, which `parse_owner_ask` refuses to render.
        'Which view opens first? Option "Chooser": it picks. I recommend "Chooser": it names.',
        # No recommendation.
        'Which view? Option "A": x. Option "B": y. Reply Merge it.',
        # A risk review missing its last field.
        "Risk to review: a dose label. Checked: the tests.",
    ],
)
def test_renders_owner_ask_refuses_a_line_in_neither_form(text: str) -> None:
    assert not arming.renders_owner_ask(text)
