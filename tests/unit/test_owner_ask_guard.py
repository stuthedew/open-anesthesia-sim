"""Tests for `.claude/hooks/owner_ask_guard.py`, the refusal of an unrecorded read or merge ask.

On `#1612` and `#1676` a thread read `bin/docket arm` through `head`, missed the
line saying to send the owner nothing, and sent the owner a bare "read #N and
merge it" (`PL-TLPH`). The hook refuses such a message unless `arm --owner-ask`
prints a recorded ask and the message carries it.

Two properties are under test. What it refuses: each phrasing of an ask in
`ASKS`. What it lets through: progress replies and merge reports, which a
thread sends far more often, so the allow list here is longer than the deny
list on purpose. `OWNER_ASK_GUARD_ARM` stands in for `arm`, so nothing here
reads a real branch.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "owner_ask_guard.py"
SETTINGS = REPO / ".claude" / "settings.json"

ASK_LINE = (
    'Which view opens first? Option "Chooser": the learner picks a view each run. '
    'Option "Last used": it opens where they left off. I recommend "Chooser": it names '
    "every view."
)
NOTHING = (
    "send the owner nothing: hold - send the owner nothing about this pull request yet, "
    "because no Owner-ask record says what to ask. claude/x: the Owner-read record on "
    "abc asks for the owner's read: a rule, so its pull request waits on the owner's read"
)


def _fake_arm(tmp_path: Path, code: int, said: str) -> str:
    """A stand-in for `bin/docket arm --owner-ask` that prints `said` and exits `code`."""
    script = tmp_path / "arm.py"
    script.write_text(f"import sys\nprint({said!r})\nsys.exit({code})\n", encoding="utf-8")
    return str(script)


def _decision(
    tmp_path: Path,
    text: str,
    *,
    code: int = 3,
    said: str = NOTHING,
    tool: str = "mcp__hearthbot__reply",
    tool_input: dict[str, object] | None = None,
) -> dict[str, str] | None:
    """The hook's `hookSpecificOutput` for one call, or `None` if it let the call through."""
    payload = json.dumps({"tool_name": tool, "tool_input": tool_input or {"text": text}})
    env = {**os.environ, "OWNER_ASK_GUARD_ARM": _fake_arm(tmp_path, code, said)}
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)["hookSpecificOutput"]


ASKS = (
    # What `#1676`'s thread sent, and `#1612`'s.
    "Read #1676 and merge it.",
    "PL-T2Q2 is done.\n\n1. Read #1612 and say Merge it.",
    "- Review PR #1612 when you can",
    "Please read the pull request.",
    "Could you review it before it merges?",
    "It waits on your read.",
    "#1676 is ready for your review.",
    "So its pull request waits on the owner's read.",
    "Reply **Merge it** when you are happy.",
    "Merge it once you have looked.",
    "Shall I merge?",
    "Merge #1676 now?",
)


@pytest.mark.parametrize("text", ASKS)
def test_a_reply_asking_for_a_read_without_a_recorded_ask_is_refused(
    tmp_path: Path, text: str
) -> None:
    decision = _decision(tmp_path, text)
    assert decision is not None
    assert decision["permissionDecision"] == "deny"
    reason = decision["permissionDecisionReason"]
    assert "says nothing may be sent to the owner" in reason
    assert NOTHING in reason


PROGRESS = (
    "#1688 is open as a draft, and CI is running.",
    "#1676 merged.",
    "Merged #1676 on your word.",
    "CI is green on #1688 and auto-merge is armed, so it merges on green.",
    "I read the item's brief and #1612's body before starting.",
    "I'll bring main in and merge it once the checks pass.",
    "The reviewer's comment is answered and the fix is pushed.",
)


@pytest.mark.parametrize("text", PROGRESS)
def test_a_progress_reply_is_let_through_whatever_arm_says(tmp_path: Path, text: str) -> None:
    assert _decision(tmp_path, text) is None


def test_an_ask_carrying_the_recorded_line_is_let_through(tmp_path: Path) -> None:
    """Emphasis, quote marks and line breaks around the line do not matter."""
    text = (
        "**Which view opens first?** Option “Chooser”: the learner picks a view\n"
        'each run. Option "Last used": it opens where they left off. I recommend "Chooser": '
        "it names every view.\n\nReply Merge it if you agree."
    )
    assert _decision(tmp_path, text, code=0, said=ASK_LINE) is None


def test_an_ask_without_the_recorded_line_is_refused_and_told_the_line(tmp_path: Path) -> None:
    decision = _decision(tmp_path, "Read #1688 and merge it.", code=0, said=ASK_LINE)
    assert decision is not None
    assert "does not carry it" in decision["permissionDecisionReason"]
    assert ASK_LINE in decision["permissionDecisionReason"]


def test_a_card_and_an_edit_are_read_as_a_reply_is(tmp_path: Path) -> None:
    card = {
        "question": "Merge #1688 now?",
        "options": [
            {"label": "Merge", "consequence": "It lands now."},
            {"label": "Wait", "consequence": "It waits."},
        ],
        "recommended": 0,
    }
    assert _decision(tmp_path, "", tool="mcp__hearthbot__ask_decision", tool_input=card)
    edit = {"message_id": "m", "text": "Read #1688 and merge it."}
    assert _decision(tmp_path, "", tool="mcp__hearthbot__update_message", tool_input=edit)


def test_another_tool_is_never_read(tmp_path: Path) -> None:
    text = "Read #1688 and merge it."
    assert _decision(tmp_path, text, tool="mcp__hearthbot__update_status") is None


@pytest.mark.parametrize("code", [1, 2, 127])
def test_an_arm_that_cannot_answer_lets_the_reply_through(tmp_path: Path, code: int) -> None:
    """A guard that breaks a thread's replies costs more than the round it saves."""
    assert _decision(tmp_path, "Read #1688 and merge it.", code=code) is None


def test_the_hook_is_wired_on_a_threads_reply_tools() -> None:
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    wired = [
        entry["matcher"]
        for entry in settings["hooks"]["PreToolUse"]
        for hook in entry["hooks"]
        if "owner_ask_guard.py" in hook["command"]
    ]
    assert wired == ["^mcp__hearthbot__(reply|update_message|ask_decision)$"]


KNOWN_GAPS = (
    # Phrasings `ASKS` does not name. Each is filed as an item once a thread is
    # seen sending it, and held here to the verdict it gets today.
    "Over to you for #1688.",
    "Your call on #1688.",
)


@pytest.mark.parametrize("text", KNOWN_GAPS)
def test_a_known_gap_is_let_through_today(tmp_path: Path, text: str) -> None:
    assert _decision(tmp_path, text) is None
