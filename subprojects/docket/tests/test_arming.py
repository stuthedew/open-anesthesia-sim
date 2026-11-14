"""Tests for what `bin/docket arm` prints, read from `arming.Verdict.lines`.

The branch-reading half of `arm` is tested through the command in
`test_cli.py`'s `test_arm_` tests. These pin the printed advice on its own
and the hold on blind review passes that no record says ran (`PL-HDRN`).
"""

from __future__ import annotations

import re
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


# A repository for the tests of the blind review hold, which call `arming.arm`
# with the count stubbed.

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


def _arm(root: Path, blind: Callable[[], arming.CommandCount] | None = None) -> arming.Verdict:
    return arming.arm(root, items_dir="docs/items", now=NOW, fetch=False, blind_count=blind)


NOT_NEEDED = "Owner-read: not needed - a refactor with its outputs pinned"


# How `arm` holds a simulator change whose blind generalist review passes have
# no record (`PL-HDRN`). The count is stubbed, because what
# `tools/blind_review.py --count` counts is pinned by its own tests.

PASSES_TWO = "Blind-review: pass 1: blocking fixed, optional rejected; pass 2: should-fix filed"
PASS_ONE = "Blind-review: pass 1: none"
OLDER_TWO = "Blind-review: passes 2, findings 3, fixed 1, filed 1, rejected 1"


def test_arm_holds_without_blind_review(tmp_path: Path) -> None:
    """Missing passes hold, a record of too few still holds, and enough passes arm.

    A fix made after the passes leaves the record standing, because close-out
    step 9 says a fix made for a finding needs no further pass.
    """
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")
    _record(git, NOT_NEEDED)
    owed = arming.CommandCount(count=2)

    held = _arm(root, lambda: owed)

    assert held.answer == arming.HOLD
    assert held.lines[0] == (
        "hold - claude/prose: it owes 2 blind review passes, and no Blind-review record says "
        "any ran"
    )
    assert arming.BLIND_ASK in held.lines

    short = _record(git, PASS_ONE)

    again = _arm(root, lambda: owed)

    assert again.answer == arming.HOLD
    assert again.lines[0].endswith(
        f"it owes 2 blind review passes, and the Blind-review record on {short[:12]} records 1"
    )

    _record(git, PASSES_TWO)

    assert _arm(root, lambda: owed).answer == arming.ARM

    _change(root, git, SIMULATOR, "X = 2\n")
    _record(git, NOT_NEEDED)

    assert _arm(root, lambda: owed).answer == arming.ARM


def test_arm_holds_again_when_the_passes_owed_rise(tmp_path: Path) -> None:
    """A record of one pass no longer covers a branch that later owes two."""
    root, git = _repo(tmp_path)
    _change(root, git, "src/anesthesia_sim/app/panel.py", "X = 1\n")
    _record(git, NOT_NEEDED, PASS_ONE)

    assert _arm(root, lambda: arming.CommandCount(count=1)).answer == arming.ARM

    held = _arm(root, lambda: arming.CommandCount(count=2))

    assert held.answer == arming.HOLD
    assert "it owes 2 blind review passes" in held.lines[0]


def test_arm_holds_when_blind_count_fails(tmp_path: Path) -> None:
    """A count that could not be read holds, so a branch is never armed as owing no pass."""
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")
    _record(git, NOT_NEEDED, PASSES_TWO)

    held = _arm(root, lambda: arming.CommandCount(declined="`blind_review --count` exited 1"))

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
    _record(git, NOT_NEEDED, "Blind-review: pass 1: blocking fixed; pass 2: blocking fixed rpeat")

    held = _arm(root, lambda: arming.CommandCount(count=2))

    assert held.answer == arming.HOLD
    assert "no Blind-review record says any ran" in held.lines[0]
    assert any(
        "could not be read (pass 2: 'blocking fixed rpeat' is not 'severity outcome [repeat]')"
        in line
        for line in held.lines
    )


def test_an_older_blind_record_still_counts_its_passes(tmp_path: Path) -> None:
    """A record in the totals form, which 28 merged pull requests carry, still covers the branch."""
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")
    _record(git, NOT_NEEDED, OLDER_TWO)

    assert _arm(root, lambda: arming.CommandCount(count=2)).answer == arming.ARM


def test_a_change_outside_the_simulator_asks_for_no_blind_count(tmp_path: Path) -> None:
    root, git = _repo(tmp_path)
    _change(root, git, "tools/script.py", "X = 1\n")

    def blind() -> arming.CommandCount:
        raise AssertionError("the passes of a change outside the simulator were counted")

    assert _arm(root, blind).answer == arming.ARM


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


# How a `Blind-review` value is read: one entry per finding, by pass (`PL-0BRY`).


def test_the_per_finding_form_is_read_by_pass() -> None:
    record = arming.parse_blind_review(
        "pass 1: blocking fixed, optional rejected; pass 2: blocking fixed repeat, "
        "should-fix   filed; pass 3: none"
    )

    assert record.passes == 3
    assert record.totals is None
    assert record.split == (
        (arming.BlindFinding("blocking", "fixed"), arming.BlindFinding("optional", "rejected")),
        (
            arming.BlindFinding("blocking", "fixed", repeat=True),
            arming.BlindFinding("should-fix", "filed"),
        ),
        (),
    )


def test_the_older_totals_form_counts_its_passes_and_splits_nothing() -> None:
    record = arming.parse_blind_review("passes 2, findings 7, fixed 7, filed 1, rejected 0")

    assert record == arming.BlindRecord(2, totals=arming.BlindTotals(7, 7, 1, 0))


@pytest.mark.parametrize(
    ("value", "reason"),
    [
        ("", "'' is not 'pass N: ...'"),
        ("pass 2: none", "pass 2 is out of order: expected pass 1"),
        ("pass 1: none; pass 1: none", "pass 1 is out of order: expected pass 2"),
        ("pass 1: blocking fixed repeat", "pass 1 cannot repeat a finding"),
        ("pass 1: major fixed", "pass 1: 'major' is not one of blocking, should-fix, optional"),
        ("pass 1: blocking done", "pass 1: 'done' is not one of fixed, filed, rejected"),
        ("pass 1: blocking", "pass 1: 'blocking' is not 'severity outcome [repeat]'"),
        ("pass 1: blocking fixed,", "pass 1: '' is not 'severity outcome [repeat]'"),
        ("passes 2", "'passes 2' is not 'pass N: ...'"),
    ],
)
def test_a_blind_record_that_cannot_be_read_says_why(value: str, reason: str) -> None:
    with pytest.raises(ValueError, match=re.escape(reason)):
        arming.parse_blind_review(value)


ASK_VALUE = (
    "Should learners read the shorter uptake step? | Shorter: the step is one paragraph; "
    "cost: it drops the worked example | As it was: learners keep the worked example; cost: "
    "the step stays three paragraphs long | recommend Shorter - every figure is unchanged, "
    "and the example repeats the figure above it | context - the uptake step is reworded | "
    "why - it changes what learners read about the uptake model, which only you approve | "
    "checked - every figure still matches its source"
)


def test_a_review_question_prints_each_part_on_its_own_line() -> None:
    """Each part of a question to the owner is a line of its own (`PL-M2JP`).

    On #2096 the owner was sent a review's four parts as one paragraph, its
    question also saying why it was theirs and that nothing needed deciding,
    and found it "a little dense and hard to follow" (project owner,
    2026-11-10). So the reason the question is theirs is a field of its own.
    """
    shown, why = arming.parse_owner_ask(ASK_VALUE)

    assert why == ""
    assert shown.splitlines() == [
        "**Should learners read the shorter uptake step?**",
        '- **I recommend "Shorter":** every figure is unchanged, and the example repeats the '
        "figure above it.",
        "- **Context:** the uptake step is reworded.",
        '- **Option "Shorter":** the step is one paragraph. **Costs and risks:** it drops the worked example.',
        '- **Option "As it was":** learners keep the worked example. **Costs and risks:** the step stays three '
        "paragraphs long.",
        "- **Why it is yours:** it changes what learners read about the uptake model, which only "
        "you approve.",
        "- **Already checked:** every figure still matches its source.",
    ]


def test_a_held_pull_request_is_asked_between_the_change_and_what_it_replaced() -> None:
    """A held pull request offers the change and its alternative, never merge or hold.

    Asked whether a pull request might merge, with holding for changes as the
    other option, the owner found no gain in holding and wrote "either you
    shouldn't be asking me in the first place because it's not a real
    question, or you need to tell me what I need to make an informed
    decision" (project owner, 2026-11-14, `PL-GG4V`). So the instructions name
    what a held change is weighed against, and a record in the old review form
    is told to ask that choice.
    """
    assert "what it was chosen over" in arming.READ_ASK
    assert "the gate as changed and the gate as it was" in arming.READ_ASK
    assert "holding gains the owner nothing they can name" in arming.READ_ASK

    _, why = arming.parse_owner_ask("changed - x | why - w | checked - z")

    assert "a choice between the change and what it was chosen over" in why
    assert "holding for changes as its options" not in why


def test_every_question_to_the_owner_leads_with_its_recommendation() -> None:
    """A question to the owner carries every part the asking rule names, or is refused.

    The review form had no options and no recommendation, and the decision
    form had no context and no reason the choice was the owner's. Sessions
    left out what the form did not ask for, and the owner wrote "you are
    still asking me to make decisions without any context, recommendations,
    trade offs etc" (project owner, 2026-11-14, `PL-GG4V`). So there is one
    form, printed question first and recommendation second. Each option
    names its cost, because options that say only what they do let a session
    offer one good and one bad: "why would I ever choose the bad".
    """
    shown, why = arming.parse_owner_ask(
        "Which view opens first? | Chooser: the learner picks a view each run; cost: one "
        "more click before every case | Last used: it opens where they left off; cost: it "
        "hides the views a learner has not opened | recommend Chooser - one click is worth "
        "showing every view | context - the simulator "
        "now has three views | why - it decides what a learner sees first"
    )

    assert why == ""
    assert shown.splitlines() == [
        "**Which view opens first?**",
        '- **I recommend "Chooser":** one click is worth showing every view.',
        "- **Context:** the simulator now has three views.",
        '- **Option "Chooser":** the learner picks a view each run. **Costs and risks:** one more click before '
        "every case.",
        '- **Option "Last used":** it opens where they left off. **Costs and risks:** it hides the views a '
        "learner has not opened.",
        "- **Why it is yours:** it decides what a learner sees first.",
    ]

    missing = (
        "after its recommendation come context - <what changed, or what the choice is about> "
        "and why - <why the choice is the owner's>, then checked - <what was already checked> "
        "if anything was"
    )
    review = (
        "it is in a review form, which gave the owner no options and no recommendation; ask "
        "it as a choice between the change and what it was chosen over, each with what it "
        "gains and gives up"
    )
    assert arming.parse_owner_ask("Q? | A: x; cost: c | B: y; cost: d | recommend A - z") == (
        "",
        missing,
    )
    assert arming.parse_owner_ask(
        "Q? | A: x; cost: c | B: y; cost: d | recommend A - z | context - c"
    ) == ("", missing)
    assert arming.parse_owner_ask(
        "Q? | A: x; cost: c | B: y; cost: d | recommend A - z | why - w | context - c"
    ) == ("", missing)
    assert arming.parse_owner_ask(
        "changed - x | question - y? | why - w | checked - z | reply - v"
    ) == ("", review)
    assert arming.parse_owner_ask("changed - x | question - y? | checked - z | reply - v") == (
        "",
        review,
    )
    assert arming.parse_owner_ask("risk - x | checked - y | look - z") == ("", review)
    assert arming.parse_owner_ask(
        "Q? | A: x | B: y; cost: d | recommend A - z | context - c | why - w"
    ) == (
        "",
        "each option needs '<option>: <what it gets>; cost: <what it gives up>', so that the "
        "owner sees what every option costs, the recommended one included",
    )


def test_a_copied_refusal_log_leaves_the_recorded_ask_in_force(tmp_path: Path) -> None:
    """A copy of the guard refusals made after the question leaves the question in force.

    `docket record` copies the refusals a branch met into `docket.toml`'s
    `record_dir`. That copy is a record, like an item file, so an `Owner-ask`
    made before it still says what to ask. Read as worked change, it made the
    gate ask for the question again (`PL-1XQP`).
    """
    root, git = _repo(tmp_path)
    _change(root, git, SIMULATOR, "X = 1\n")
    _record(git, "Owner-read: needed - a change to the uptake model", f"Owner-ask: {ASK_VALUE}")
    _change(root, git, "docs/hook-blocks/claude-prose.tsv", "refused\n")

    def ask(record_dir: str) -> arming.Verdict:
        return arming.arm(
            root,
            items_dir="docs/items",
            record_dir=record_dir,
            now=NOW,
            fetch=False,
            owner_ask=True,
        )

    assert ask("docs/hook-blocks").sendable is not None
    assert ask("").unasked
