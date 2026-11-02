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
import re
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
    code: int = 3,
    said: str = NOTHING,
    tool: str = "mcp__hearthbot__post_message",
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
    # Hand-offs beside a pull request, the gaps `#1688` first shipped with.
    "Over to you for #1688.",
    "Your call on #1688.",
    "Over to you on the pull request.",
    "Up to you whether #1688 goes in.",
    "#1688 is your decision.",
    "PR #1688: your call.",
    "Let me know about #1688.",
    "Thoughts on #1688?",
    # A noun hand-off that only looks like a report of a recorded decision is
    # still an ask (`PL-YGR6`): a question in the gap, a decision still to come,
    # or a real hand-off in the same message as a report.
    "Your call on whether #1688 is applied.",
    "Your choice on #1700 is applied when you merge it.",
    "Recorded your choice; #1700 is your call.",
    # A hold put in the future is still an ask when its sentence names a pull
    # request, or its subject is "it", "this" or "that" (`PL-VHMS`).
    "#1945 will wait for your read.",
    "The pull request will wait for your read.",
    "It will wait for your read.",
    "This'll need your review before it merges.",
    "Each part is drafted. Each will wait for your read, starting with #1945.",
)


@pytest.mark.parametrize("text", ASKS)
def test_a_reply_asking_for_a_read_without_a_recorded_ask_is_refused(
    tmp_path: Path, text: str
) -> None:
    decision = _decision(tmp_path, text)
    assert decision is not None
    assert decision["permissionDecision"] == "deny"
    reason = decision["permissionDecisionReason"]
    assert "It carries no Owner-ask line" in reason
    assert NOTHING in reason
    assert MISTAKEN in reason


PROGRESS = (
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
    # A hand-off in quote marks is a mention, here from a reply listing what the
    # hook counts, which the hook refused (`PL-XR8B`).
    'It refuses twenty ask phrasings including "over to you" and "your call" beside a '
    "pull request.",
    "The hand-offs are “over to you” and ‘your call’ when a sentence names a PR.",
    # A hold put in the future, for pull requests not yet opened, which the hook
    # refused on 2026-11-02 (`PL-VHMS`).
    "Because each one changes MODEL.md, each will wait for your read.",
    "Both would need your review once they are open.",
    "#1944 merged. The next parts are going to be ready for your read later today.",
)


@pytest.mark.parametrize("text", PROGRESS)
def test_a_progress_reply_is_let_through_whatever_arm_says(tmp_path: Path, text: str) -> None:
    assert _decision(tmp_path, text) is None


REPORTS = (
    # The two status reports the hook refused during the v0.6.0 cut (`PL-YGR6`).
    "Your choice on the card is recorded on the item, and auto-merge is on for #1700.",
    "Recorded your choice on PL-9CS6; the release pull request #1700 is armed.",
    # The same class in other words: the hand-off as the subject of a recording
    # verb, and as its object.
    "Your decision on #1700 has been noted, and it merges on green.",
    "I applied your call to the item, so #1688 is armed.",
)


@pytest.mark.parametrize("text", REPORTS)
def test_a_report_of_a_choice_already_made_is_let_through(tmp_path: Path, text: str) -> None:
    """A noun hand-off that reports a recorded decision asks for nothing.

    The asks that only look like such a report, such as "Your call on whether
    #1688 is applied.", are rows of `ASKS` above.
    """
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
    assert MISTAKEN in decision["permissionDecisionReason"]


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


@pytest.mark.parametrize("code", [1, 2, 127])
def test_an_arm_that_cannot_answer_falls_back_to_the_rendered_line_check(
    tmp_path: Path, code: int
) -> None:
    """A broken `arm` no longer lets a bare ask through, and blocks nothing else."""
    assert _decision(tmp_path, "Read #1688 and merge it.", code=code, said="") is not None
    assert _decision(tmp_path, f"The thread asks: {ASK_LINE}", code=code, said="") is None
    assert _decision(tmp_path, "#1688 merged.", code=code, said="") is None


def test_the_hook_is_wired_on_every_projects_tool() -> None:
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    wired = [
        entry["matcher"]
        for entry in settings["hooks"]["PreToolUse"]
        for hook in entry["hooks"]
        if "owner_ask_guard.py" in hook["command"]
    ]
    assert len(wired) == 1
    for tool in (*MESSAGE_TOOLS, "mcp__hearthbot__send_card"):
        assert re.search(wired[0], tool), tool
    assert not re.search(wired[0], "mcp__github__add_issue_comment")


POST = "mcp__hearthbot__post_message"

#: The risk-review form of the line `arm --owner-ask` prints.
RISK_LINE = (
    "Risk to review: a dose label could read mg for mcg. Checked: the formatter tests pin "
    "the unit. Please look at: the infusion panel's label."
)


#: What `arm --owner-ask` prints in the coordinator's checkout, on no branch.
NO_BRANCH = (
    "send the owner nothing: unknown - HEAD is on no branch, so there is no pull request "
    "to answer for"
)


def test_a_bare_ask_where_arm_cannot_answer_for_the_branch_is_refused(tmp_path: Path) -> None:
    """The coordinator's checkout is on no pull request's branch, so `arm` cannot answer there.

    The coordinator and a thread both post with `post_message`, so the hook
    asks `arm` about every ask. Where `arm` has no recorded line, the post
    needs a line in the rendered `Owner-ask` form (`PL-YV90`, `PL-YN60`).
    """
    decision = _decision(tmp_path, "Read #1700 and merge it.", code=3, said=NO_BRANCH, tool=POST)
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
    assert _decision(tmp_path, text, code=3, said=NO_BRANCH, tool=POST) is None


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
