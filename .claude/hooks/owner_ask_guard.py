"""PreToolUse hook on the Projects tools: attach the recorded question to a message about a held PR.

**What it does** (`PL-X4MD`). A thread's message that names a pull request,
sent while this checkout's pull request waits on the owner's read, leaves
carrying what `bin/docket arm --owner-ask` records for it:

- **A question for the owner is recorded (exit 0).** Where the message does
  not already hold that line word for word, the hook appends it.
- **None is recorded (exit `NO_ASK`).** The hook appends `NONE_RECORDED`, which
  tells the owner there is nothing to decide yet.
- **Any other answer, or none.** The message goes out untouched. That covers
  a pull request that waits on no read, and the coordinator's checkout, which
  is on no pull request's branch. The coordinator quotes the thread's recorded
  question itself, as `.claude/skills/docket/modes/coordinator.md` says.

A message that names no pull request goes out untouched, and `arm` is not
asked. The hook refuses nothing. A progress note that names a held pull
request carries the question too, which the owner accepted as the cost of
never refusing a message for its wording (project owner, 2026-11-03,
ratified, over the wording match this replaced, `PL-X4MD`).

**Why it rewrites instead of refusing.** The guard before it decided which
messages were asks by matching their wording against a list of phrasings.
Wording is a guess: one version refused ordinary progress notes, and the one
after it let through an ask phrased in words the list did not hold
(`PL-TLPH`, `PL-3D2F`). Whether a pull request waits on the owner, and what
it asks, is already recorded, so the hook reads that record and renders it
into the message, rather than checking that the thread typed it.

**How the rewrite reaches the owner.** The hook returns
`permissionDecision: "allow"` with `updatedInput`, the call's whole input with
`text` changed, and an `additionalContext` telling the session what it added.
A Projects thread checked on 2026-11-04 that the stored message carries the
appended line (`PL-X4MD` § "Step 1 passed"). `"allow"` is needed because, in
auto mode, Claude Code can deny a changed call that carries no decision and
then drops the `updatedInput` on the retry
(https://code.claude.com/docs/en/hooks, § "PreToolUse `updatedInput` in auto
mode", read 2026-11-03). The cost is that the hook approves these sends
itself. `guard.py` still refuses the call where another guard refuses it.

**Which tools.** Every `mcp__hearthbot__` tool but those in
`NOT_TO_THE_OWNER`, whose text goes to another session or names a thread
(`PL-YN60`). The rewrite needs a top-level `text` string, which
`post_message` and `edit_message` take. A call naming a held pull request
with no such field, such as a decision card, goes out unchanged, and the
session is told the question was not attached.

**Fails open** on a payload that is not JSON, and where `arm` is missing,
times out or exits with a status it does not define. `guard.py` reports an
error in the hook itself as a note (`PL-9KSJ`). `OWNER_ASK_GUARD_ARM` names a
Python script run in place of `arm` for the tests, and is set nowhere else.
`NO_ASK` and `EXIT` are read from `docket.arming`, found through
`shell_split.py` as the Bash guards find it, and imported only for a message
that names a pull request, since `guard.py` runs this before every MCP call
(`PL-NDY5`).

Standard library only, since a hook runs before any virtualenv is known.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hook_input
import shell_split  # noqa: F401 - puts docket's src on sys.path

#: The prefix of every Projects tool. The hook is wired on all of them.
PROJECTS_TOOL = "mcp__hearthbot__"

#: The Projects tools whose text does not reach the owner as a message: a
#: message to another session, or a thread's name. Every other Projects tool is
#: read, so a tool the harness renames or adds is read until it is named
#: here (`PL-YN60`). Names read from a thread's tool list on 2026-11-02.
NOT_TO_THE_OWNER = frozenset(
    PROJECTS_TOOL + name for name in ("message_coordinator", "message_thread", "rename_thread")
)

#: The input field the rewrite changes. `post_message` takes only `text`, read
#: from a thread's call on 2026-11-04, and `edit_message` takes it beside the
#: message's id.
TEXT_FIELD = "text"

#: A pull request named by number, "#1950", or by name, "pull request" or "PR".
# regex: a pull request reference in free prose, where no parser applies.
NAMES_PULL_REQUEST = re.compile(r"#\d+\b|\bpull[ \t]+requests?\b|\bPRs?\b", re.IGNORECASE)

#: What the hook appends where the pull request waits on the owner's read and
#: no question for them is recorded (`PL-X4MD`, the owner's wording).
NONE_RECORDED = "No question is recorded on this pull request yet, so there is nothing to decide."

#: How long `arm` may take. Its question for this hook answered in 0.3 s on a
#: one-file branch on 2026-11-03, against 1.6 s for the full answer
#: (`PL-3D2F`). The wiring gives the pre-mcp group room for it, so this leaves
#: time to fail open rather than be cut off.
ARM_TIMEOUT_S = 45


def every_string(value: object) -> list[str]:
    """Every string in `value`, at any depth of its dictionaries and lists, in order."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [found for item in value.values() for found in every_string(item)]
    if isinstance(value, list):
        return [found for item in value for found in every_string(item)]
    return []


def to_the_owner(tool_name: str) -> bool:
    """Whether a call to `tool_name` shows the owner its text."""
    return tool_name.startswith(PROJECTS_TOOL) and tool_name not in NOT_TO_THE_OWNER


def squeezed(said: str) -> str:
    """`said` without Markdown emphasis, its quote marks straight and its spacing single."""
    said = said.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    return " ".join(said.translate(str.maketrans("", "", "*_`>")).split())


def carries(text: str, line: str) -> bool:
    """Whether `text` holds `line` word for word, ignoring emphasis, case and spacing."""
    return squeezed(line).casefold() in squeezed(text).casefold()


def owner_ask(root: Path) -> tuple[int, str] | None:
    """The exit status and first line of `bin/docket arm --no-fetch --owner-ask`, or None.

    None where `arm` cannot be run, times out, prints nothing, or exits with a
    status its answers do not use, which means it failed.
    """
    from docket.arming import EXIT, NO_ASK
    from docket.lines import split_lines

    override = os.environ.get("OWNER_ASK_GUARD_ARM")
    command = (
        [sys.executable, override]
        if override
        else [str(root / "bin" / "docket"), "arm", "--no-fetch", "--owner-ask"]
    )
    try:
        done = subprocess.run(
            command, cwd=root, capture_output=True, timeout=ARM_TIMEOUT_S, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode not in {0, NO_ASK, *EXIT.values()}:
        return None
    lines = [
        line.strip() for line in split_lines(done.stdout.decode("utf-8", "replace")) if line.strip()
    ]
    if not lines:
        return None
    return done.returncode, lines[0]


def recorded_line(root: Path) -> str | None:
    """The line the owner is to be sent about this checkout's pull request, or None.

    It is the recorded question where `arm` has one, `NONE_RECORDED` where the
    pull request waits on the owner's read with none, and None where it waits
    on no read or `arm` cannot say.
    """
    from docket.arming import NO_ASK

    answer = owner_ask(root)
    if answer is None:
        return None
    code, line = answer
    if code == 0:
        return line
    if code == NO_ASK:
        return NONE_RECORDED
    return None


def decide(payload: str) -> str:
    """The rewrite of a Projects call that names a held pull request, a note, or ""."""
    try:
        call = json.loads(payload)
    except ValueError:
        return ""
    if not isinstance(call, dict):
        return ""
    tool_name = str(call.get("tool_name", ""))
    tool_input = call.get("tool_input")
    if not to_the_owner(tool_name) or not isinstance(tool_input, dict):
        return ""
    shown = "\n".join(every_string(tool_input))
    if NAMES_PULL_REQUEST.search(shown) is None:
        return ""
    line = recorded_line(hook_input.project_root())
    if line is None or carries(shown, line):
        return ""
    text = tool_input.get(TEXT_FIELD)
    if not isinstance(text, str):
        return hook_input.output(
            "PreToolUse",
            notes=[
                "owner_ask_guard: this message names a pull request that waits on the owner's "
                f"read, and `{tool_name}` has no `{TEXT_FIELD}` field to attach its line to, so "
                f"the owner sees the message without it. The line is:\n\n    {line}"
            ],
        )
    rewritten = {**tool_input, TEXT_FIELD: text.rstrip() + "\n\n" + line}
    return hook_input.output(
        "PreToolUse",
        rewrite=rewritten,
        notes=[
            "owner_ask_guard added this line to the end of the message, because this "
            "checkout's pull request waits on the owner's read and the message did not "
            f"carry it (`PL-X4MD`):\n\n    {line}"
        ],
    )
