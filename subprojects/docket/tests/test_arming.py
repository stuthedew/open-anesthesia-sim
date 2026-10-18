"""Tests for what `bin/docket arm` prints, read from `arming.Verdict.lines`.

The branch-reading half of `arm` is tested through the command in
`test_cli.py`'s `test_arm_` tests. These pin the printed advice on its own.
"""

from __future__ import annotations

from datetime import UTC, datetime

from docket import arming
from docket.claims import Hold

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
