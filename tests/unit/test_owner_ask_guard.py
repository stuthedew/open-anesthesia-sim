"""Tests for `.claude/hooks/owner_ask_guard.py`, which attaches the recorded question to a message.

A message that names a pull request, sent while the checkout's pull request
waits on the owner's read, leaves carrying what `bin/docket arm --owner-ask`
records: the question for the owner, or a line saying none is recorded
(`PL-X4MD`). Every other message goes out untouched, and none is refused.
`OWNER_ASK_GUARD_ARM` stands in for `arm`, so nothing here reads a real
branch. The calls run through `.claude/hooks/guard.sh`, the entry point every
guard shares, so what is checked is the output Claude Code receives.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import guard as entry_point
import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "guard.sh"
#: The guard these tests run alone, through the entry point every guard shares.
GUARD = "owner_ask_guard"
SETTINGS = REPO / ".claude" / "settings.json"
POST = "mcp__hearthbot__post_message"

#: The decision form of the question `arm --owner-ask` prints, exiting 0, one
#: line for each of its parts.
ASK_LINE = (
    "Which view opens first?\n"
    '- Option "Chooser": the learner picks a view each run.\n'
    '- Option "Last used": it opens where they left off.\n'
    '- I recommend "Chooser": it names every view.'
)
#: What `arm --owner-ask` prints, exiting 3, where the pull request waits on
#: the owner's read with no question recorded.
NOTHING = (
    "send the owner nothing: hold - send the owner nothing about this pull request yet, "
    "because no Owner-ask record says what to ask."
)
#: What it prints, exiting 1, where nothing holds the pull request.
NOT_HELD = (
    "not held - claude/x does not wait on the owner's read, so there is no ask to send "
    "them; `bin/docket arm` says whether it may be armed"
)
#: What it prints, exiting 2, in the coordinator's checkout on no branch.
NO_BRANCH = "unknown - HEAD is on no branch, so there is no pull request to answer for"
#: What the hook appends where no question is recorded, in the owner's words.
NONE_RECORDED = "No question is recorded on this pull request yet, so there is nothing to decide."


def _fake_arm(tmp_path: Path, code: int, said: str) -> str:
    """A stand-in for `bin/docket arm --owner-ask` that prints `said` and exits `code`."""
    script = tmp_path / "arm.py"
    script.write_text(f"import sys\nprint({said!r})\nsys.exit({code})\n", encoding="utf-8")
    return str(script)


def _output(
    tmp_path: Path,
    text: str,
    *,
    code: int = 0,
    said: str = ASK_LINE,
    tool: str = POST,
    tool_input: dict[str, object] | None = None,
    group: str = GUARD,
) -> dict[str, object] | None:
    """The `hookSpecificOutput` for one call, or `None` where the hook printed nothing."""
    payload = json.dumps({"tool_name": tool, "tool_input": tool_input or {"text": text}})
    env = {**os.environ, "OWNER_ASK_GUARD_ARM": _fake_arm(tmp_path, code, said)}
    result = subprocess.run(
        ["bash", str(HOOK), group],
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
    output: dict[str, object] = json.loads(result.stdout)["hookSpecificOutput"]
    return output


def _sent(output: dict[str, object] | None) -> str | None:
    """The message text a rewrite sends, or `None` where the call goes out unchanged."""
    if output is None or "updatedInput" not in output:
        return None
    assert output["permissionDecision"] == "allow"
    rewritten = output["updatedInput"]
    assert isinstance(rewritten, dict)
    text = rewritten["text"]
    assert isinstance(text, str)
    return text


def test_an_ask_about_a_waiting_pull_request_carries_the_recorded_question(tmp_path: Path) -> None:
    """The case `PL-X4MD` is for: the owner reads the question in the message itself."""
    output = _output(tmp_path, "#1950 is ready.")
    assert _sent(output) == "#1950 is ready.\n\n" + ASK_LINE
    assert output is not None
    assert ASK_LINE in str(output["additionalContext"])


def test_a_held_pull_request_with_no_question_says_there_is_nothing_to_decide(
    tmp_path: Path,
) -> None:
    """A bare "read #N" reaches the owner saying no question is recorded (`PL-X4MD`)."""
    assert _sent(_output(tmp_path, "Read #1950 and merge it.", code=3, said=NOTHING)) == (
        "Read #1950 and merge it.\n\n" + NONE_RECORDED
    )


def test_a_message_already_carrying_the_question_goes_out_unchanged(tmp_path: Path) -> None:
    quoted = "\n".join(f"> {line}" for line in ASK_LINE.upper().splitlines())
    text = f"Decision for **#1950**:\n\n{quoted}"
    assert _output(tmp_path, text) is None


def test_a_message_carrying_only_the_first_line_of_the_question_gets_the_whole_of_it(
    tmp_path: Path,
) -> None:
    """The hook attaches every line of the question, not the first alone (`PL-M2JP`)."""
    first = ASK_LINE.splitlines()[0]
    assert _sent(_output(tmp_path, f"#1950: {first}")) == f"#1950: {first}\n\n" + ASK_LINE


@pytest.mark.parametrize(
    ("code", "said"), [(1, NOT_HELD), (2, NO_BRANCH)], ids=["not-held", "coordinator"]
)
def test_a_pull_request_that_waits_on_no_read_leaves_the_message_alone(
    tmp_path: Path, code: int, said: str
) -> None:
    """The coordinator's checkout is on no pull request's branch, so it lands here too."""
    assert _output(tmp_path, "Read #1950 and merge it.", code=code, said=said) is None


@pytest.mark.parametrize("code", [5, 127])
def test_an_arm_that_fails_leaves_the_message_alone(tmp_path: Path, code: int) -> None:
    assert _output(tmp_path, "Read #1950 and merge it.", code=code, said="") is None


def test_a_message_naming_no_pull_request_never_asks_arm(tmp_path: Path) -> None:
    """`arm` takes up to a second and a half, so a message with no pull request skips it."""
    marker = tmp_path / "arm-ran"
    script = tmp_path / "arm.py"
    script.write_text(f"open({str(marker)!r}, 'w')\nprint('x')\n", encoding="utf-8")
    payload = json.dumps({"tool_name": POST, "tool_input": {"text": "Started the next item."}})
    result = subprocess.run(
        ["bash", str(HOOK), GUARD],
        input=payload,
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "OWNER_ASK_GUARD_ARM": str(script)},
        check=False,
    )
    assert result.stdout.strip() == ""
    assert not marker.exists()


@pytest.mark.parametrize(
    "text", ["See #1950.", "The pull request is up.", "Opened a PR for it.", "Two PRs are open."]
)
def test_each_way_of_naming_a_pull_request_is_read(tmp_path: Path, text: str) -> None:
    assert _sent(_output(tmp_path, text)) == text + "\n\n" + ASK_LINE


def test_an_edit_keeps_its_other_fields_and_gets_the_line(tmp_path: Path) -> None:
    """`updatedInput` replaces the whole input, so every other field is copied (`PL-X4MD`)."""
    edit = {"message_id": "cmsg_1", "text": "#1950 is ready."}
    output = _output(tmp_path, "", tool="mcp__hearthbot__edit_message", tool_input=edit)
    assert output is not None
    assert output["updatedInput"] == {
        "message_id": "cmsg_1",
        "text": "#1950 is ready.\n\n" + ASK_LINE,
    }


def test_a_card_with_no_text_field_goes_out_unchanged_and_the_session_is_told(
    tmp_path: Path,
) -> None:
    card = {"question": "Merge #1950 now?", "options": [{"label": "Merge"}, {"label": "Wait"}]}
    output = _output(tmp_path, "", tool="mcp__hearthbot__request_decision", tool_input=card)
    assert output is not None
    assert "updatedInput" not in output
    assert "permissionDecision" not in output
    assert "has no `text` field" in str(output["additionalContext"])


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
    assert _output(tmp_path, "Read #1950 and merge it.", tool=tool) is None


def test_a_projects_tool_the_hook_has_never_seen_is_read(tmp_path: Path) -> None:
    """A renamed or new tool is read until it is named as one that does not reach the owner."""
    assert _sent(_output(tmp_path, "#1950.", tool="mcp__hearthbot__send_card")) is not None


def test_nothing_is_refused_for_its_wording(tmp_path: Path) -> None:
    """The phrasings the old wording match refused now go out, with the line attached."""
    for text in ("It waits on your read.", "Shall I merge #1950?", "#1950 is your call."):
        output = _output(tmp_path, text, code=3, said=NOTHING)
        assert output is None or output.get("permissionDecision") != "deny", text


def test_a_rewrite_reaches_the_owner_through_the_whole_mcp_group(tmp_path: Path) -> None:
    """Run as Claude Code runs it: every pre-mcp guard on one call, merged into one output."""
    output = _output(tmp_path, "#1950 is ready.", group="pre-mcp")
    assert _sent(output) == "#1950 is ready.\n\n" + ASK_LINE


def test_the_hook_is_wired_on_every_projects_tool() -> None:
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    wired = [
        entry["matcher"]
        for entry in settings["hooks"]["PreToolUse"]
        for hook in entry["hooks"]
        if hook["command"] == 'bash "$CLAUDE_PROJECT_DIR/.claude/hooks/guard.sh" pre-mcp'
    ]
    assert len(wired) == 1
    for tool in (POST, "mcp__hearthbot__edit_message", "mcp__hearthbot__send_card"):
        # regex: the matcher is a regular expression to Claude Code, so it is read as one.
        assert re.search(wired[0], tool), tool
    assert GUARD in [guard.name for guard in entry_point.GROUPS["pre-mcp"]]
