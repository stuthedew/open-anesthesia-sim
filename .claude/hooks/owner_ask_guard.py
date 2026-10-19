"""PreToolUse hook on a Projects thread's reply tools: refuse an unrecorded read or merge ask.

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
sessions have used and the closing-block lines that carry them. A phrasing it
misses is a known gap, held as a row in `tests/unit/test_owner_ask_guard.py`,
and a message that matches by accident is told to reword. A false refusal
costs a rewording, while a missed ask costs the owner's attention, so the list
leans toward refusing.

**Not wired on the coordinator's `post_message`.** The coordinator's checkout
is not the pull request's branch, so `arm` cannot answer for it there.

**Fails open where it cannot answer**: a payload it cannot read, a `bin/docket`
that is missing, times out or exits with anything but 0 or 3. A guard that
breaks a thread's replies costs more than the round it saves. `arm`'s own
`unknown` exits 3 under `--owner-ask`, and is refused, because then nobody can
say an ask is recorded. `OWNER_ASK_GUARD_ARM` names a Python script run in place of
`arm` for the tests, and is set nowhere else. `NO_ASK` is read from
`docket.arming`, found through `shell_split.py` as the Bash guards find it.

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
from docket.arming import NO_ASK
from docket.lines import split_lines

#: The tools whose text reaches the owner in a thread, with the fields that carry it.
TEXT_FIELDS = {
    "mcp__hearthbot__reply": ("text",),
    "mcp__hearthbot__update_message": ("text",),
    "mcp__hearthbot__ask_decision": ("question", "context", "reason"),
}

#: Where an imperative starts: a line, a list item or a sentence.
_START = r"(?:^[ \t]*(?:[-*+]|\d+[.)])?[ \t]*|[.!?:;][ \t]+)"

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
    )
)

#: How long `arm` may take. It answered in 2.2 s on 2026-10-19; the wiring
#: gives the hook 60 s, so this leaves room to fail open rather than be cut off.
ARM_TIMEOUT_S = 45


def message_text(tool_name: str, tool_input: object) -> str | None:
    """The text a call would show the owner, or None for a tool this hook does not read."""
    fields = TEXT_FIELDS.get(tool_name)
    if fields is None or not isinstance(tool_input, dict):
        return None
    parts = [tool_input.get(field) for field in fields]
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


def carries(text: str, line: str) -> bool:
    """Whether `text` holds `line` word for word, ignoring emphasis, case and spacing."""

    def squeezed(said: str) -> str:
        return " ".join(plain(said).split()).casefold()

    return squeezed(line) in squeezed(text)


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
            "it is refused (PL-TLPH)."
        )
    return (
        opening + "`bin/docket arm --owner-ask` says nothing may be sent to the owner about this "
        f"branch's pull request:\n\n    {line}\n\n"
        "So send no read or merge ask. Run `bin/docket arm` and read all of its output, "
        "not through head or tail: it says what to do. Usually that is to record "
        "`Owner-read: not needed - <why>` so the change merges on green, or, for a real "
        "decision or a high-risk change, to record an `Owner-ask:` and then send the line "
        "arm prints. If this message is not an ask, reword it so that it does not read "
        "as one. On #1612 and #1676 a bare ask reached the owner this way (PL-TLPH)."
    )


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except ValueError:
        return 0
    if not isinstance(payload, dict):
        return 0
    text = message_text(str(payload.get("tool_name", "")), payload.get("tool_input"))
    if not text:
        return 0
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
