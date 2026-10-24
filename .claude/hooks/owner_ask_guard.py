"""PreToolUse hook on the Projects reply and post tools: refuse an unrecorded read or merge ask.

**What it refuses** (`PL-TLPH`). A `reply`, an `update_message` or an
`ask_decision` card whose text asks the owner to read or merge a pull request,
unless `bin/docket arm --owner-ask` prints a recorded ask for this branch and
the text carries that line word for word. Everything else passes untouched:
progress replies, merge reports, and any message that matches none of `ASKS`.

**Why a hook and not more text.** Whether the owner may be asked was text for a
session to read, three times over. `PL-9KHK` changed the wording, `PL-DKBG`
narrowed what holds, and `PL-9JHM` made the ask an `Owner-ask:` record that
`arm` prints. On `#1612` and `#1676` a session still read `arm` through `head`,
missed the line saying to send nothing, and sent the owner a bare "read #N and
merge it". Text fails whenever it is read short, so this checks the message
itself, at the one moment it goes out.

**Which pull request.** The one this checkout's branch carries, since a thread
drives the pull request of the branch it works on. `arm` answers for `HEAD`
with `--no-fetch`, so the check costs about two seconds and no fetch (measured
2026-10-19). A thread whose checkout is on another branch is refused, which is
the safe direction: the coordinator forwards the owner's word, and a thread
asks only about its own pull request.

**What an ask is, is a list, not an inference.** `ASKS` names the phrasings
sessions have used, the closing-block lines that carry them, and close
variants of each. A hand-off such as "over to you" or "your call" counts only
in a sentence that also names a pull request. A noun hand-off that reports a
decision already recorded, such as "recorded your choice" or "your choice is
recorded", does not count (`PL-YGR6`). A wording the list does not
name still passes, so a new one seen in a thread is added to `ASKS` with a
test row. A message that matches by accident is told to reword. A false
refusal costs a rewording, while a missed ask costs the owner's attention, so
the list leans toward refusing.

**The coordinator's `post_message` gets a partial check** (`PL-YV90`). The
coordinator relays a thread's ask to the owner in the project chat. Its
checkout is on no pull request's branch, so `arm` cannot answer for it there,
and this hook does not run `arm` for that tool. It refuses a post that matches
`ASKS` and carries no line in the form `bin/docket arm --owner-ask` renders.
`docket.arming.renders_owner_ask` recognizes that form from the templates the
renderer uses, so the hook holds no copy of it. Nobody has read the tool's
schema, so the hook reads every string in the post's input, at any depth
(`PL-646J`). The check cannot tell the
recorded line from a well-formed wrong one. Having `arm` answer for a named
pull request would, at the cost of a fetch and a worktree per post (project
owner, 2026-10-24, ratified, over building that now). Nobody has seen that
failure, and this check would become that route's first stage.

**Fails open where it cannot answer**: a payload it cannot read, a `bin/docket`
that is missing, times out or exits with anything but 0 or 3. A guard that
breaks a thread's replies costs more than the round it saves. `arm`'s own
`unknown` exits 3 under `--owner-ask`, and is refused, because then nobody can
say an ask is recorded. `OWNER_ASK_GUARD_ARM` names a Python script run in place of
`arm` for the tests, and is set nowhere else. `NO_ASK` is read from
`docket.arming`, found through `shell_split.py` as the Bash guards find it,
and so is `renders_owner_ask`.

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
from docket.arming import NO_ASK, renders_owner_ask
from docket.lines import split_lines

#: The coordinator's post to the project chat, which gets the partial check.
COORDINATOR_POST = "mcp__hearthbot__post_message"

#: The tools whose text reaches the owner, with the fields that carry it.
#: `None` reads every string in the call's input, at any depth of its
#: dictionaries and lists. `post_message`'s schema could not be read from the
#: session that wired it on 2026-10-24, so the hook does not guess which field
#: holds the text, or how deep that field sits (`PL-646J`).
TEXT_FIELDS: dict[str, tuple[str, ...] | None] = {
    "mcp__hearthbot__reply": ("text",),
    "mcp__hearthbot__update_message": ("text",),
    "mcp__hearthbot__ask_decision": ("question", "context", "reason"),
    COORDINATOR_POST: None,
}

#: Where an imperative starts: a line, a list item or a sentence.
_START = r"(?:^[ \t]*(?:[-*+]|\d+[.)])?[ \t]*|[.!?:;][ \t]+)"

#: Verbs that report a decision the owner has already made, as in "recorded
#: your choice" or "your choice is recorded". A noun hand-off in either of
#: those forms is a status report, not an ask. The hook refused two such
#: reports during the v0.6.0 cut on 2026-10-20 (`PL-YGR6`). The list is short
#: on purpose: a report worded some other way is still refused, which is the
#: direction this hook leans.
_RECORDED = ("recorded", "noted", "applied", "logged", "saved", "followed", "implemented")

#: A noun hand-off that is the subject of a recording verb in the passive:
#: "your choice on the card is recorded", "your call has been noted". At most
#: three words may come between the noun and the verb, and none of them may
#: start a question, so "your call on whether #1688 is applied" is still an ask.
#: A verb followed by "when", "once", "after", "if" or "as soon" describes a
#: decision still to come, so "your choice is applied when you merge #1700" is
#: still an ask too.
_REPORTED_AFTER = (
    r"(?!(?:[ \t]+(?:on|for|about|in|from|at)"
    r"(?:[ \t]+(?!(?:whether|if|which|what|how|who|when)\b)[\w#'-]+){1,3})?"
    r"[ \t]+(?:is|was|has[ \t]+been|have[ \t]+been)[ \t]+(?:now[ \t]+)?"
    r"(?:" + "|".join(_RECORDED) + r")\b"
    r"(?![ \t]+(?:when|once|after|if|as[ \t]+soon)\b))"
)

#: A noun hand-off that is the object of a recording verb: "recorded your
#: choice". Python's lookbehind needs a fixed width, so each verb gets its own,
#: with exactly one space or tab before "your".
_REPORTED_BEFORE = "".join(rf"(?<!\b{verb}[ \t])" for verb in _RECORDED)

#: Words that hand a decision to the owner. They are an ask only beside a pull
#: request, since "the colour is your call" asks for no read. A hand-off just
#: after a quote mark is a mention, as in a reply listing what the hook counts,
#: which this hook refused on 2026-10-19 (`PL-XR8B`). A noun hand-off that
#: reports a recorded decision is not one either (`_RECORDED`).
_HANDOFF = (
    r"(?<![\"'])\b(?:over[ \t]+to[ \t]+you|up[ \t]+to[ \t]+you"
    r"|"
    + _REPORTED_BEFORE
    + r"your[ \t]+(?:call|decision|choice|go)\b"
    + _REPORTED_AFTER
    + r"|let[ \t]+me[ \t]+know|thoughts[ \t]+on|what[ \t]+do[ \t]+you[ \t]+think)\b"
)

#: A pull request named by number or by name.
_PULL_REQUEST = r"(?:#\d+|\bpull[ \t]+requests?\b|\bprs?\b)"

#: The text between two phrases in one sentence: no sentence end or line break.
_SAME_SENTENCE = r"[^.!?\n]{0,80}?"

#: The phrasings of an ask to read or merge a pull request (`PL-TLPH`). Each is
#: matched case-insensitively against the text with its Markdown emphasis
#: removed.
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
        r"\b(?:waiting|waits|wait|awaiting|awaits|needs|need|ready)[ \t]+(?:(?:for|on)[ \t]+)?"
        r"your[ \t]+(?:read|review|approval|merge|go-ahead)\b",
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

#: How long `arm` may take. It answered in 2.2 s on 2026-10-19; the wiring
#: gives the hook 60 s, so this leaves room to fail open rather than be cut off.
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


def message_text(tool_name: str, tool_input: object) -> str | None:
    """The text a call would show the owner, or None for a tool this hook does not read."""
    if tool_name not in TEXT_FIELDS or not isinstance(tool_input, dict):
        return None
    fields = TEXT_FIELDS[tool_name]
    if fields is None:
        return "\n".join(every_string(tool_input))
    parts = [tool_input.get(f) for f in fields]
    options = tool_input.get("options")
    if isinstance(options, list):
        for option in options:
            if isinstance(option, dict):
                parts += [option.get("label"), option.get("consequence")]
    return "\n".join(part for part in parts if isinstance(part, str))


def plain(text: str) -> str:
    """`text` without Markdown emphasis, quote marks made straight, for matching."""
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    return re.sub(r"[*_`>]", "", text)


def asked(text: str) -> str | None:
    """The first phrase in `text` that asks the owner to read or merge, or None."""
    shown = plain(text)
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
    if done.returncode not in (0, NO_ASK):
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


def coordinator_refusal(text: str) -> str | None:
    """Why the coordinator's post may not go to the owner, or None to let it through.

    It runs no `arm`, because the coordinator's checkout is on no pull
    request's branch. It checks only that an ask carries a line in a rendered
    `Owner-ask:` form (`PL-YV90`).
    """
    phrase = asked(text)
    if phrase is None or renders_owner_ask(squeezed(text)):
        return None
    return (
        f'This post asks the owner to read or merge a pull request ("{phrase}"), and it '
        "carries no Owner-ask line. Forward the thread's Owner-ask line word for word, the "
        "line `bin/docket arm --owner-ask` prints on the thread's branch, or send the owner "
        "nothing about that pull request. A bare 'read #N' relayed from here costs the owner "
        "as much attention as one sent from a thread (PL-YV90)." + mistaken(phrase)
    )


def refusal(text: str, root: Path) -> str | None:
    """Why this message may not go to the owner, or None to let it through."""
    phrase = asked(text)
    if phrase is None:
        return None
    answer = owner_ask(root)
    if answer is None:
        return None
    code, line = answer
    if code == 0 and carries(text, line):
        return None
    opening = f'This message asks the owner to read or merge a pull request ("{phrase}"). '
    if code == 0:
        return (
            opening + "This branch has a recorded Owner-ask, but the message does not carry it. "
            "Open the ask with this line, word for word, and keep the rest short:\n\n"
            f"    {line}\n\n"
            "That line is what the owner judges, so a bare 'read #N' or 'Merge it' without "
            "it is refused (PL-TLPH)." + mistaken(phrase)
        )
    return (
        opening + "`bin/docket arm --owner-ask` says nothing may be sent to the owner about this "
        f"branch's pull request:\n\n    {line}\n\n"
        "So send no read or merge ask. Run `bin/docket arm` and read all of its output, "
        "not through head or tail: it says what to do. Usually that is to record "
        "`Owner-read: not needed - <why>` so the change merges on green, or, for a real "
        "decision or a high-risk change, to record an `Owner-ask:` and then send the line "
        "arm prints. On #1612 and #1676 a bare ask reached the owner this way (PL-TLPH)."
        + mistaken(phrase)
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
    if tool_name == COORDINATOR_POST:
        reason = coordinator_refusal(text)
    else:
        reason = refusal(text, hook_input.project_root())
    if reason is None:
        return 0
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    # A broken guard must never block a reply.
    except Exception:
        sys.exit(0)
