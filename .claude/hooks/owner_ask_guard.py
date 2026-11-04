"""PreToolUse hook on the Projects tools: refuse a message the owner should not be sent yet.

**What it checks: an ask, and only an ask** (`PL-TLPH`, `PL-3D2F`). A message
asks when it holds one of the phrasings in `ASKS`, such as "Read #1676 and
merge it" or "It waits on your read", or a question in the form that `arm
--owner-ask` renders. `docket.arming.renders_owner_ask` recognizes that form
from the renderer's own templates, so the hook holds no copy of it. Any other
message goes through without `arm` being asked. That includes a progress note
that names a pull request, because the hook exists to stop asks that are not
real questions, never to filter what else a thread says (project owner,
2026-11-03).

**What "not a real question" means here.** The owner calls these
"non-questions". It is an ask that carries no recorded question: a bare
request to read, merge or review a pull request, or a question written into
the message when no `Owner-ask` record backs it. A recorded question is the
decision or review line that `bin/docket arm --owner-ask` prints. The hook
cannot judge whether a recorded question is worth asking. A question with an
obvious answer still passes once it is recorded, and only `arm`'s printed
instructions to the session guard against that.

**What an ask needs is what `arm` records** (`PL-3D2F`). For an ask, the hook
asks `bin/docket arm --owner-ask` about this checkout's branch:

- **Held for the owner's read, with no `Owner-ask` recorded (exit 3).** The
  ask is refused, whatever its form. A question written into the message is
  refused too (`PL-R1HT`). The way past the refusal is to record an
  `Owner-ask:` trailer, or `Owner-read: not needed - <why>` where the change
  needs no read.
- **An ask recorded (exit 0).** The ask must carry the recorded line word for
  word.
- **Any other answer, or none.** The ask must carry a line in the recorded
  form. This is the coordinator's check: it relays a thread's ask from a
  checkout on no pull request's branch, where `arm` cannot answer
  (`PL-YV90`).

**The state decides, and the wording only finds the ask** (`PL-3D2F`). A
message that holds an ask phrasing in a sentence that asks nothing, such as
"no longer needs your read", is refused, and the refusal says to reword it
and record the mistake. The hook checks the message itself, at the moment it
goes out, because a session that reads `arm`'s output short misses the line
saying to send nothing (`PL-TLPH`).

**Which tools: every Projects tool but a named few** (`PL-YN60`). The hook is
wired on every `mcp__hearthbot__` tool and reads every string in the call's
input, at any depth. It skips only the tools in `NOT_TO_THE_OWNER`, whose text
goes to another session or names a thread. Naming the skipped tools means a
renamed or new tool is checked until someone says otherwise.
Nobody has read these tools' schemas, so the hook does not guess which field
holds the text (`PL-646J`).

**What it cannot check.** The coordinator's check cannot tell the recorded line
from a well-formed wrong one. Having `arm` answer for a named pull request
would, at the cost of a fetch and a worktree per post (project owner,
2026-10-24, ratified, over building that now). Nobody has seen that failure.

**Fails open only where it cannot read the call**: a payload that is not
JSON, or an error in the hook itself. A guard that breaks a thread's replies
costs more than the round it saves. A `bin/docket` that is missing, times out
or exits with a status it does not define falls back to the coordinator's
check, which refuses only an ask. `OWNER_ASK_GUARD_ARM` names a Python script
run in place of `arm` for the tests, and is set nowhere else. `NO_ASK`,
`EXIT` and `renders_owner_ask` are read from `docket.arming`, found through
`shell_split.py` as the Bash guards find it.

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

# isort: split
from docket.arming import EXIT, NO_ASK, renders_owner_ask
from docket.lines import split_lines

#: The prefix of every Projects tool. The hook is wired on all of them.
PROJECTS_TOOL = "mcp__hearthbot__"

#: The Projects tools whose text does not reach the owner as a message: a
#: message to another session, or a thread's name. Every other Projects tool is
#: read, so a tool the harness renames or adds is checked until it is named
#: here (`PL-YN60`). Names read from a thread's tool list on 2026-11-02.
NOT_TO_THE_OWNER = frozenset(
    PROJECTS_TOOL + name for name in ("message_coordinator", "message_thread", "rename_thread")
)

#: Where an imperative starts: a line, a list item or a sentence.
_START = r"(?:^[ \t]*(?:[-*+]|\d+[.)])?[ \t]*|[.!?:;][ \t]+)"

#: Words that hand a decision to the owner. They are an ask only beside a pull
#: request, since "the colour is your call" asks for no read.
_HANDOFF = (
    r"\b(?:over[ \t]+to[ \t]+you|up[ \t]+to[ \t]+you|your[ \t]+(?:call|decision|choice|go)"
    r"|let[ \t]+me[ \t]+know|thoughts[ \t]+on|what[ \t]+do[ \t]+you[ \t]+think)\b"
)

#: A pull request named by number or by name.
_PULL_REQUEST = r"(?:#\d+|\bpull[ \t]+requests?\b|\bprs?\b)"

#: The text between two phrases in one sentence: no sentence end or line break.
_SAME_SENTENCE = r"[^.!?\n]{0,80}?"

#: A pull request held for the owner: "It waits on your read", "#1676 is ready
#: for your review".
HOLD_FOR_YOUR_READ = (
    r"\b(?:waiting|waits|wait|awaiting|awaits|needs|need|ready)[ \t]+"
    r"(?:(?:for|on)[ \t]+)?your[ \t]+(?:read|review|approval|merge|go-ahead)\b"
)

#: The phrasings of an ask to read or merge a pull request (`PL-TLPH`). Each
#: is matched case-insensitively against the text with its Markdown emphasis
#: removed. A quoted, negated or foretold phrase still matches: the context
#: rules that let those through were deleted in `PL-3D2F`.
ASKS = tuple(
    re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    for pattern in (
        # "Read #1676 and merge it", "Please review PR #1612".
        _START + r"(?:please[ \t]+)?(?:read|review|look[ \t]+(?:at|over))[ \t]+"
        r"(?:and[ \t]+merge[ \t]+)?(?:(?:the[ \t]+)?(?:pull[ \t]+request|pr)[ \t]+)?#\d+",
        # "Read the pull request", "Review this PR".
        _START + r"(?:please[ \t]+)?(?:read|review)[ \t]+(?:the|this|its|my)[ \t]+"
        r"(?:pull[ \t]+request|pr)\b",
        # "Could you read it", "please merge".
        r"\b(?:please|can[ \t]+you|could[ \t]+you|would[ \t]+you)[ \t]+"
        r"(?:read|review|merge|approve)\b",
        # "It waits on your read", "ready for your review".
        HOLD_FOR_YOUR_READ,
        # `arm`'s own words, copied into a reply.
        r"\bwaits?[ \t]+on[ \t]+the[ \t]+owner'?s[ \t]+read\b",
        # "Say Merge it", "reply 'Merge it'".
        r"\b(?:say|reply|send|type|give|answer|tap)[ \t]+(?:me[ \t]+)?[\"']?merge[ \t]+it\b",
        # "Merge it when you have read it."
        _START + r"merge[ \t]+it\b",
        # "Shall I merge?", "Merge #1676?"
        r"\b(?:shall|should|can|may)[ \t]+i[ \t]+(?:go[ \t]+ahead[ \t]+and[ \t]+)?merge\b",
        r"\bmerge[ \t]+(?:(?:pull[ \t]+request|pr)[ \t]+)?#\d+[ \t]*(?:now[ \t]*)?\?",
        # "Over to you for #1688", "#1688 is your call": a hand-off and a pull
        # request named in one sentence, in either order.
        _HANDOFF + _SAME_SENTENCE + _PULL_REQUEST,
        _PULL_REQUEST + _SAME_SENTENCE + _HANDOFF,
    )
)

#: How long `arm` may take. Its question for this hook answered in 0.3 s on a
#: one-file branch on 2026-11-03, against 1.6 s for the full answer
#: (`PL-3D2F`). The wiring gives the hook 60 s, so this leaves room to fail
#: open rather than be cut off.
ARM_TIMEOUT_S = 45

#: The exit statuses of `arm --owner-ask` that answer the question: 0 for a
#: recorded ask, `NO_ASK` for a hold for the owner's read with none, and the
#: statuses of its other answers. Any other status means `arm` itself failed.
ANSWERED = frozenset({0, NO_ASK, *EXIT.values()})


def every_string(value: object) -> list[str]:
    """Every string in `value`, at any depth of its dictionaries and lists, in order."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [found for item in value.values() for found in every_string(item)]
    if isinstance(value, list):
        return [found for item in value for found in every_string(item)]
    return []


def message_text(tool_name: str, tool_input: object) -> str | None:
    """The text a call would show the owner, or None for a tool this hook does not read."""
    if not tool_name.startswith(PROJECTS_TOOL) or tool_name in NOT_TO_THE_OWNER:
        return None
    if not isinstance(tool_input, dict):
        return None
    return "\n".join(every_string(tool_input))


def plain(text: str) -> str:
    """`text` without Markdown emphasis, quote marks made straight, for matching."""
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    return re.sub(r"[*_`>]", "", text)


def asked(text: str) -> str | None:
    """The first phrase in `text` that asks the owner to read or merge, or None.

    A backtick is read as a space, so "Read `#1950`" is still an ask.
    """
    shown = plain(text.replace("`", " "))
    for pattern in ASKS:
        found = pattern.search(shown)
        if found is not None:
            return found.group(0).strip(" \t.!?:;-*+")
    return None


def squeezed(said: str) -> str:
    """`said` without emphasis, its quote marks straight and its spacing single, for matching."""
    return " ".join(plain(said).split())


def carries(text: str, line: str) -> bool:
    """Whether `text` holds `line` word for word, ignoring emphasis, case and spacing."""
    return squeezed(line).casefold() in squeezed(text).casefold()


def owner_ask(root: Path) -> tuple[int, str] | None:
    """The exit status and first line of `bin/docket arm --no-fetch --owner-ask`, or None."""
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
    if done.returncode not in ANSWERED:
        return None
    lines = [
        line.strip() for line in split_lines(done.stdout.decode("utf-8", "replace")) if line.strip()
    ]
    if not lines:
        return None
    return done.returncode, lines[0]


def mistaken(phrase: str) -> str:
    """What to do when the message was not an ask, so a wrong refusal is recorded.

    The refused session is the only one that sees a refusal, and it would
    otherwise reword and carry on, so a pattern of wrong refusals would never
    reach the owner. Filing an item leaves a record that outlives the session,
    and `bin/docket` flags a title filed more than once (project owner,
    2026-10-19, ratified, over a shared refusal log or no record, `PL-TLPH`).
    """
    quoted = phrase.replace('"', "'")
    return (
        "\n\nIf this message is not an ask, the hook is wrong. Record that before "
        "rewording, with:\n\n"
        f'    bin/docket new "owner_ask_guard.py refused a message that asked for nothing: '
        f'{quoted}"\n\n'
        "Then reword the message so that it does not read as an ask."
    )


def refusal(text: str, root: Path) -> str | None:
    """Why this message may not go to the owner, or None to let it through.

    Only an ask is checked: a phrasing in `ASKS`, or a question in the form
    `arm --owner-ask` renders. Any other message, such as a progress note,
    goes through without `arm` being asked.
    """
    phrase = asked(text)
    posed = renders_owner_ask(squeezed(text))
    if phrase is None and not posed:
        return None
    what = f'("{phrase}")' if phrase is not None else "(a question in the recorded form)"
    wrong = mistaken(phrase) if phrase is not None else ""
    answer = owner_ask(root)
    if answer is not None and answer[0] == NO_ASK:
        return (
            f"This message asks the owner to read, merge or decide something {what}, and this "
            "checkout's pull request waits on the owner's read with no Owner-ask record saying "
            f"what to ask. `bin/docket arm --owner-ask` says:\n\n    {answer[1]}\n\n"
            "Run `bin/docket arm` and read all of its output. Where the owner has something to "
            "decide or review, record it as an `Owner-ask:` trailer and send the line arm then "
            "prints. Where the change needs no read, record `Owner-read: not needed - <why>`, "
            "and it merges on green. A question written into the message without that record "
            "is refused too (PL-R1HT)." + wrong
        )
    if answer is not None and answer[0] == 0:
        line = answer[1]
        if carries(text, line):
            return None
        return (
            f"This message asks the owner to read, merge or decide something {what}, and this "
            "checkout's pull request has a recorded Owner-ask that the message does not carry. "
            "Open the ask with this line, word for word, and keep the rest short:\n\n"
            f"    {line}\n\n"
            "That line is what the owner judges, so a bare 'read #N', 'Merge it' or another "
            "question without it is refused (PL-TLPH)." + wrong
        )
    if posed:
        return None
    said = (
        f"`bin/docket arm --owner-ask` says, for this checkout's branch:\n\n    {answer[1]}\n\n"
        if answer is not None
        else "`bin/docket arm --owner-ask` gave no answer for this checkout's branch.\n\n"
    )
    return (
        f'This message asks the owner to read or merge a pull request ("{phrase}"). '
        "It carries no Owner-ask line. " + said + "When relaying a thread's ask, forward the "
        "thread's Owner-ask line word for word, or send the owner nothing about that pull "
        "request. On a thread's own branch, run `bin/docket arm` and read all of its output, "
        "not through head or tail: it says what to do. On #1612 and #1676 a bare ask reached "
        "the owner (PL-TLPH)." + wrong
    )


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except ValueError:
        return 0
    if not isinstance(payload, dict):
        return 0
    tool_name = str(payload.get("tool_name", ""))
    text = message_text(tool_name, payload.get("tool_input"))
    if not text:
        return 0
    reason = refusal(text, hook_input.project_root())
    if reason is None:
        return 0
    sys.stdout.write(
        hook_input.deny("owner_ask_guard", "bare-read-ask", reason, json.dumps(payload))
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    # A broken guard must never block a reply.
    except Exception:
        sys.exit(0)
