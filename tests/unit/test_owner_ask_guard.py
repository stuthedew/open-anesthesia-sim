"""Tests for `.claude/hooks/owner_ask_guard.py`, which holds back what the owner should not get.

On `#1612` and `#1676` a thread read `bin/docket arm` through `head`, missed the
line saying to send the owner nothing, and sent the owner a bare "read #N and
merge it" (`PL-TLPH`). The hook now keys on what `arm --owner-ask` answers for
the checkout's branch (`PL-3D2F`), and these tests cover each answer. Held for
the owner's read with no recorded ask, every message is refused. With an ask
recorded, a message naming a pull request must carry it. Otherwise, the
coordinator's check refuses an ask in `ASKS`'s phrasings that carries no line
in the recorded form. `OWNER_ASK_GUARD_ARM` stands in for `arm`, so nothing
here reads a real branch.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import guard as entry_point
import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "guard.sh"
#: The guard these tests run alone, through the entry point every guard shares.
GUARD = "owner_ask_guard"
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

#: What `arm --owner-ask` prints, and exits 2 with, in the coordinator's
#: checkout on no branch.
NO_BRANCH = "unknown - HEAD is on no branch, so there is no pull request to answer for"

#: The refusal's instruction for a message that was not an ask.
MISTAKEN = "If this message is not an ask, the hook is wrong. Record that before rewording"


def _fake_arm(tmp_path: Path, code: int, said: str) -> str:
    """A stand-in for `bin/docket arm --owner-ask` that prints `said` and exits `code`."""
    script = tmp_path / "arm.py"
    script.write_text(f"import sys\nprint({said!r})\nsys.exit({code})\n", encoding="utf-8")
    return str(script)


def _decision(
    tmp_path: Path,
    text: str,
    *,
    code: int = 2,
    said: str = NO_BRANCH,
    tool: str = "mcp__hearthbot__post_message",
    tool_input: dict[str, object] | None = None,
) -> dict[str, str] | None:
    """The hook's `hookSpecificOutput` for one call, or `None` if it let the call through."""
    payload = json.dumps({"tool_name": tool, "tool_input": tool_input or {"text": text}})
    env = {**os.environ, "OWNER_ASK_GUARD_ARM": _fake_arm(tmp_path, code, said)}
    result = subprocess.run(
        ["bash", str(HOOK), GUARD],
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


#: What `arm --owner-ask` prints, and exits 1 with, where nothing holds the
#: pull request for the owner's read.
NOT_HELD = (
    "not held - claude/x does not wait on the owner's read, so there is no ask to send "
    "them; `bin/docket arm` says whether it may be armed"
)


#: Asks from a thread held for the owner's read with no recorded ask. Each is
#: refused. The first is `PL-R1HT`'s reproduction, a hand-written question in
#: the recorded form, which the hook let through while `arm` exited 3 for
#: every state with nothing to send. The others are bare read and merge asks.
HELD = (
    'Which unit should the label show? Option "mcg": keeps the label short. Option "mg": '
    'matches the pump. I recommend "mcg": it is what the item specifies.',
    "Read #1950 and merge it.",
    "It waits on your read.",
    "Please review the pull request.",
)


@pytest.mark.parametrize("text", HELD)
def test_a_waiting_threads_ask_is_refused_until_it_records_one(tmp_path: Path, text: str) -> None:
    """In this state no ask may reach the owner, however it is put (`PL-R1HT`, `PL-3D2F`)."""
    decision = _decision(tmp_path, text, code=3, said=NOTHING)
    assert decision is not None
    assert decision["permissionDecision"] == "deny"
    reason = decision["permissionDecisionReason"]
    assert "waits on the owner's read with no Owner-ask record" in reason
    assert NOTHING in reason


def test_a_waiting_threads_card_and_edit_are_read_as_a_post_is(tmp_path: Path) -> None:
    card = {"question": "Merge #1950 now?", "options": [{"label": "Merge"}, {"label": "Wait"}]}
    for tool, tool_input in (
        ("mcp__hearthbot__request_decision", card),
        ("mcp__hearthbot__edit_message", {"message_id": "m", "text": "Read #1950 and merge it."}),
    ):
        assert _decision(tmp_path, "", code=3, said=NOTHING, tool=tool, tool_input=tool_input)


def test_a_held_threads_message_to_the_coordinator_is_not_read(tmp_path: Path) -> None:
    """The coordinator decides what reaches the owner, so the thread may still tell it."""
    tool = "mcp__hearthbot__message_coordinator"
    assert _decision(tmp_path, "Read #1950 and merge it.", code=3, said=NOTHING, tool=tool) is None


def test_an_ask_carrying_the_recorded_line_is_let_through(tmp_path: Path) -> None:
    """Emphasis, quote marks and line breaks around the line do not matter."""
    text = (
        "**Which view opens first?** Option “Chooser”: the learner picks a view\n"
        'each run. Option "Last used": it opens where they left off. I recommend "Chooser": '
        "it names every view.\n\nReply Merge it for #1688 if you agree."
    )
    assert _decision(tmp_path, text, code=0, said=ASK_LINE) is None


@pytest.mark.parametrize(
    "text",
    [
        "Read #1688 and merge it.",
        "#1688 is ready for your review.",
        'The thread asks: Which unit? Option "mcg": short. Option "mg": the pump. I recommend '
        '"mcg": the item says so.',
    ],
)
def test_an_ask_without_the_recorded_line_is_refused_where_one_is_recorded(
    tmp_path: Path, text: str
) -> None:
    """The last row is a question in the recorded form that is not this branch's line."""
    decision = _decision(tmp_path, text, code=0, said=ASK_LINE)
    assert decision is not None
    reason = decision["permissionDecisionReason"]
    assert "has a recorded Owner-ask that the message does not carry" in reason
    assert ASK_LINE in reason


def test_a_progress_note_never_asks_arm(tmp_path: Path) -> None:
    """A message that asks nothing goes through without `arm` being run at all.

    The stand-in `arm` here fails the test if it runs, by printing a line
    the hook would refuse on and exiting 3.
    """
    marker = tmp_path / "arm-ran"
    script = tmp_path / "arm.py"
    script.write_text(
        f"import pathlib, sys\npathlib.Path({str(marker)!r}).touch()\nprint('x')\nsys.exit(3)\n",
        encoding="utf-8",
    )
    payload = json.dumps(
        {"tool_name": "mcp__hearthbot__post_message", "tool_input": {"text": "#1950 is green."}}
    )
    env = {**os.environ, "OWNER_ASK_GUARD_ARM": str(script)}
    result = subprocess.run(
        ["bash", str(HOOK), GUARD],
        input=payload,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert not result.stdout.strip()
    assert not marker.exists()


#: The phrasings of an ask that the coordinator's check refuses when no line in
#: the recorded form comes with them.
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
    "Read `#1950` and merge it.",
    # Hand-offs beside a pull request, the gaps `#1688` first shipped with.
    "Over to you for #1688.",
    "Your call on #1688.",
    "Over to you on the pull request.",
    "Up to you whether #1688 goes in.",
    "#1688 is your decision.",
    "PR #1688: your call.",
    "Let me know about #1688.",
    "Thoughts on #1688?",
)


@pytest.mark.parametrize("code", [1, 2])
@pytest.mark.parametrize("text", ASKS)
def test_an_ask_with_no_recorded_line_is_refused_where_nothing_is_held(
    tmp_path: Path, text: str, code: int
) -> None:
    said = NOT_HELD if code == 1 else NO_BRANCH
    decision = _decision(tmp_path, text, code=code, said=said)
    assert decision is not None
    assert decision["permissionDecision"] == "deny"
    reason = decision["permissionDecisionReason"]
    assert "It carries no Owner-ask line" in reason
    assert said in reason
    assert MISTAKEN in reason


#: Phrases that the hook let through before `PL-3D2F`, because they were quoted,
#: negated, about a decision card, foretold, or reported a recorded choice. The
#: hook no longer reads context, so each holds an ask phrasing and is refused.
#: The refusal says to reword the message and record the mistake.
NO_LONGER_EXEMPT = (
    'The hook\'s rows quote "over to you" beside a pull request.',
    "Nothing below needs your read now.",
    "#1950 no longer needs your review; I withdrew the ask.",
    "The code edit is waiting on your go-ahead on the decision card.",
    "Because each one changes MODEL.md, each will wait for your read.",
    "Recorded your choice on PL-9CS6; the release pull request #1700 is armed.",
)


@pytest.mark.parametrize("text", NO_LONGER_EXEMPT)
def test_the_coordinators_check_reads_no_context_around_an_ask(tmp_path: Path, text: str) -> None:
    assert _decision(tmp_path, text, code=1, said=NOT_HELD) is not None


#: Messages that ask for nothing. They go through in every state `arm` can be
#: in, including a pull request waiting on the owner's read (project owner,
#: 2026-11-03: the hook should never catch progress updates).
PROGRESS = (
    "Tests are running; I will report back.",
    "Done for today.",
    "#1950 is green.",
    "The PR is finished and CI passed.",
    "#1688 is open as a draft, and CI is running.",
    "#1676 merged.",
    "Merged #1676 on your word.",
    "CI is green on #1688 and auto-merge is armed, so it merges on green.",
    "I read the item's brief and #1612's body before starting.",
    "I'll bring main in and merge it once the checks pass.",
    "The reviewer's comment is answered and the fix is pushed.",
    # A hand-off with no pull request in its sentence asks for no read.
    "The colour is your call; I chose blue as a placeholder.",
    "Whether to cut a release later is up to you.",
    "#1688 merged. What colour to use next is your call.",
    "Over to the coordinator for #1688's merge.",
    "I'll let you know when #1688 is green.",
    "Your PR template is not used here.",
)


@pytest.mark.parametrize(
    ("code", "said"), [(0, ASK_LINE), (1, NOT_HELD), (2, NO_BRANCH), (3, NOTHING)]
)
@pytest.mark.parametrize("text", PROGRESS)
def test_a_progress_reply_is_let_through_in_every_state(
    tmp_path: Path, text: str, code: int, said: str
) -> None:
    assert _decision(tmp_path, text, code=code, said=said) is None


def test_a_refusal_says_how_to_record_that_it_was_wrong(tmp_path: Path) -> None:
    """The refused session is the only one that sees a refusal, so it files a wrong one."""
    decision = _decision(tmp_path, 'Reply "Merge it" when you are happy.')
    assert decision is not None
    assert (
        '    bin/docket new "owner_ask_guard.py refused a message that asked for nothing: '
        "Reply 'Merge it\"" in decision["permissionDecisionReason"]
    )


#: The Projects tools that carry a thread's messages, read from a thread's tool
#: list on 2026-11-02. They replaced `reply`, `update_message` and
#: `ask_decision`, which the hook named until `PL-YN60`.
MESSAGE_TOOLS = (
    "mcp__hearthbot__post_message",
    "mcp__hearthbot__edit_message",
    "mcp__hearthbot__request_decision",
)


def test_a_card_and_an_edit_are_read_as_a_post_is(tmp_path: Path) -> None:
    """The hook let both through while it named the tools by their old names (`PL-YN60`)."""
    card = {
        "question": "Merge #1688 now?",
        "options": [
            {"label": "Merge", "consequence": "It lands now."},
            {"label": "Wait", "consequence": "It waits."},
        ],
        "recommended": 0,
    }
    assert _decision(tmp_path, "", tool="mcp__hearthbot__request_decision", tool_input=card)
    edit = {"message_id": "m", "text": "Read #1688 and merge it."}
    assert _decision(tmp_path, "", tool="mcp__hearthbot__edit_message", tool_input=edit)


def test_a_projects_tool_the_hook_has_never_seen_is_read(tmp_path: Path) -> None:
    """A renamed or new tool is checked until it is named as one that does not reach the owner."""
    text = "Read #1688 and merge it."
    assert _decision(tmp_path, text, tool="mcp__hearthbot__send_card") is not None


@pytest.mark.parametrize(
    "tool",
    [
        "mcp__hearthbot__message_coordinator",
        "mcp__hearthbot__message_thread",
        "mcp__hearthbot__rename_thread",
        "mcp__github__add_issue_comment",
    ],
)
def test_a_tool_whose_text_does_not_reach_the_owner_is_never_read(
    tmp_path: Path, tool: str
) -> None:
    assert _decision(tmp_path, "Read #1688 and merge it.", tool=tool) is None


@pytest.mark.parametrize("code", [5, 127])
def test_an_arm_that_fails_falls_back_to_the_coordinators_check(tmp_path: Path, code: int) -> None:
    """A broken `arm` lets no bare ask through, and blocks nothing else."""
    assert _decision(tmp_path, "Read #1688 and merge it.", code=code, said="") is not None
    assert _decision(tmp_path, f"The thread asks: {ASK_LINE}", code=code, said="") is None
    assert _decision(tmp_path, "#1688 merged.", code=code, said="") is None


def test_the_hook_is_wired_on_every_projects_tool() -> None:
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    wired = [
        entry["matcher"]
        for entry in settings["hooks"]["PreToolUse"]
        for hook in entry["hooks"]
        if hook["command"] == 'bash "$CLAUDE_PROJECT_DIR/.claude/hooks/guard.sh" pre-mcp'
    ]
    assert len(wired) == 1
    for tool in (*MESSAGE_TOOLS, "mcp__hearthbot__send_card"):
        assert re.search(wired[0], tool), tool
    assert GUARD in [guard.name for guard in entry_point.GROUPS["pre-mcp"]]


POST = "mcp__hearthbot__post_message"

#: The review form of the line `arm --owner-ask` prints.
RISK_LINE = (
    "What changed: the dose label reads mcg. Question for you: should it show mcg/kg/min? "
    "Already checked: the label matches the unit stored. What to reply: Merge it."
)


def test_a_bare_ask_where_arm_cannot_answer_for_the_branch_is_refused(tmp_path: Path) -> None:
    """The coordinator's checkout is on no pull request's branch, so `arm` cannot answer there.

    The coordinator and a thread both post with `post_message`, so the hook
    asks `arm` about every ask. Where `arm` has no recorded line, the post
    needs a line in the rendered `Owner-ask` form (`PL-YV90`, `PL-YN60`).
    """
    decision = _decision(tmp_path, "Read #1700 and merge it.", code=2, said=NO_BRANCH, tool=POST)
    assert decision is not None
    reason = decision["permissionDecisionReason"]
    assert "carries no Owner-ask line" in reason
    assert "forward the thread's Owner-ask line word for word" in reason
    assert NO_BRANCH in reason
    assert MISTAKEN in reason


@pytest.mark.parametrize("line", [ASK_LINE, RISK_LINE])
def test_a_coordinator_post_carrying_a_rendered_owner_ask_line_is_let_through(
    tmp_path: Path, line: str
) -> None:
    """Either form passes, with emphasis and a line break inside it, when `arm` records no ask."""
    wrapped = line.replace(". ", ".\n", 1)
    text = f"The thread on #1700 asks:\n\n**{wrapped}**\n\nReply Merge it if you agree."
    assert _decision(tmp_path, text, code=2, said=NO_BRANCH, tool=POST) is None


def test_a_post_carrying_another_branchs_line_is_refused_where_arm_records_one(
    tmp_path: Path,
) -> None:
    """A thread's own recorded ask outranks the rendered form, so a thread cannot send another."""
    text = f"The thread on #1700 asks: {RISK_LINE} Reply Merge it if you agree."
    assert _decision(tmp_path, text, code=0, said=ASK_LINE, tool=POST) is not None


def test_a_coordinator_post_asking_for_nothing_is_let_through(tmp_path: Path) -> None:
    text = "#1700 merged on green, and the thread on #1701 is working PL-JLB4."
    assert _decision(tmp_path, text, tool=POST) is None


def test_a_coordinator_post_is_read_whatever_field_carries_its_text(tmp_path: Path) -> None:
    """`post_message`'s schema was not readable when it was wired, so every string field counts."""
    post = {"channel": "project", "message": "Read #1700 and merge it."}
    assert _decision(tmp_path, "", tool=POST, tool_input=post) is not None


@pytest.mark.parametrize(
    "post",
    [
        {"channel": "project", "blocks": [{"type": "text", "text": "Read #1700 and merge it."}]},
        {"channel": "project", "message": {"body": {"markdown": "Read #1700 and merge it."}}},
    ],
)
def test_a_coordinator_post_with_its_text_in_a_nested_field_is_refused(
    tmp_path: Path, post: dict[str, object]
) -> None:
    """A string at any depth of the post's input is read, in a list or in a dictionary.

    Nobody has read `post_message`'s schema, so its text may sit below the top
    level. The hook read only the top-level strings and let both of these posts
    through (`PL-646J`).
    """
    decision = _decision(tmp_path, "", tool=POST, tool_input=post)
    assert decision is not None
    assert "carries no Owner-ask line" in decision["permissionDecisionReason"]
