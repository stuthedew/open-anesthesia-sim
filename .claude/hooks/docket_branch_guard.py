"""Say so if the base has moved, and, at the first edit that is work, if the branch claims nothing.

It runs as a `PreToolUse` guard on an edit and after each Bash call, through
`guard.py` (`PL-9KSJ`).

`PL-1CYR` made the branch-vs-`main` question askable at any moment
(`bin/docket branch`) instead of only at session start. This is what asks it,
at the one moment worth asking: a session opened to discuss the next piece of
work sits while another session merges, and the staleness would otherwise
surface at push time as a merge conflict. The first edit is where a
discussion becomes implementation, so it is where the answer is wanted.

**Once per session, not once per edit.** The check fetches, and paying for a
fetch before every edit would be a worse tax than the conflict it prevents.
The marker is keyed on the session id the hook is handed.

**It says nothing when the branch is current** (`--if-stale`). A hook that
speaks unasked has to earn each line, and "your base has not moved" is not
worth interrupting an edit for.

**It adds context; it never grants permission.** The output carries no
`permissionDecision`: sending `allow` would auto-approve the very edit this is
attached to, which is a security property, not a convenience. The hook's
whole job is to say something.

**The claim question waits for the first edit outside the queue** (`PL-J9S0`,
`PL-MB2W` § "Forgetful session"). Who holds an item is a `Claim:` trailer the
session commits, and a session that forgets to write one is invisible to
every reader of that record until CI refuses its pull request. So before the
first edit that is work, the hook adds "this branch claims nothing:
`bin/docket claim <id>`" where that is so. Not at the first edit of any kind:
a capture or a triage pass writes only the queue - its items, the roadmap,
the notes and its body record - and owes no claim, and asking then would
spend the session's one question where it had no answer.
`tools/branch_id_check.py --hint` decides, from the reader CI's refusal uses,
so the hook and the gate cannot disagree: its exit 3 says the path was not
work outside the queue and nothing was asked. Any other status spends the
question, since asking a broken check before every edit would tax each one.

**After a Bash call, it reads the tree rather than the command** (`PL-RXFK`).
A session can edit through Bash, which the harness's auto mode recommends for
small edits, and a Bash command names no path. So the hook also runs after
each Bash call: as `PostToolUse`, or as `PostToolUseFailure` where the
command failed, which is common when one command edits and then runs a check.
A clean tree means the call edited nothing yet, and the hook stops there.
Otherwise both questions are asked as they are at an edit, and the claim
question goes to `tools/branch_id_check.py --hint-changed`, which asks it of
every file the checkout has changed. A command that edits and commits in one
call leaves a clean tree, so it is asked at the next call that leaves a
change. Speaking just after the edit rather than just before it costs
nothing, because the hook adds context and blocks nothing.

**Only the run that creates a marker speaks.** The hooks for parallel tool
calls run at the same time, so each marker is created with `O_EXCL`, which
refuses a file that already exists. Without it, two parallel calls could both
fetch and both print. `GIT_OPTIONAL_LOCKS=0` keeps the hook's reads of the
tree from refreshing the index as a side effect, so they never hold the index
lock while a `git add` or `git commit` in a parallel call needs it.

**A question it could not ask is said, once** (`PL-9KSJ`). A checkout with no
`bin/docket` has nothing to ask, and a tree git cannot read is taken for one
the call left clean, so each says nothing. A `bin/docket branch` or
`tools/branch_id_check.py` that fails spends its marker, as a question that
was asked does, and the note says which one failed and how.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import hook_input

#: The events after a Bash call. Any other event, or none, is read as an edit's.
AFTER_BASH = ("PostToolUse", "PostToolUseFailure")

#: The start of the one line of docket's standard error that is kept: the
#: floor refusal, so a session below docket's Python floor is told why it
#: hears nothing.
FLOOR_REFUSAL = "docket needs Python"

#: The characters a session id keeps in a marker's filename.
SAFE = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")


def _safe(value: object) -> str:
    """`value` reduced to the characters in `SAFE`, or "" where it is not a string."""
    return "".join(c for c in value if c in SAFE) if isinstance(value, str) else ""


def _create(marker: Path) -> bool:
    """Create `marker`, and say whether this run made it rather than finding it there."""
    try:
        os.close(os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644))
    except OSError:
        return False
    return True


def _text(stream: bytes) -> str:
    """A command's output as text. It is read as bytes, so a `\\r` stays a `\\r` (`PL-0R4M`)."""
    return stream.decode("utf-8", "replace")


def _failed(what: str, done: subprocess.CompletedProcess[bytes]) -> str:
    """The sentence saying `what` could not be asked, with the exit status and last error line."""
    last = _text(done.stderr).strip().rpartition("\n")[2]
    return f"The branch guard could not ask {what}: it exited {done.returncode}" + (
        f" ({last})." if last else "."
    )


def _edited_path(fields: dict[str, object]) -> str:
    """The path an edit's documented `tool_input` names, from the four edit tools, or ""."""
    edit = fields.get("tool_input")
    if not isinstance(edit, dict):
        return ""
    for key in ("file_path", "notebook_path"):
        value = edit.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def decide(payload: str) -> str:
    """The note to add before an edit or after a Bash call, or "" where there is none."""
    root = hook_input.project_root()
    docket = root / "bin" / "docket"
    if not os.access(docket, os.X_OK):
        return ""
    # The id and the event are read as JSON as the rest of the payload is, so
    # an id laid out on the line after its key is still the id (`PL-CXK6`). A
    # payload that is not JSON or names no id shares the markers kept for
    # "unknown": the first such session is asked, and the rest are not.
    try:
        data = json.loads(payload)
    except ValueError:
        data = None
    fields: dict[str, object] = data if isinstance(data, dict) else {}
    session = _safe(fields.get("session_id")) or "unknown"
    named = fields.get("hook_event_name")
    event = named if isinstance(named, str) and named in AFTER_BASH else "PreToolUse"
    markers = Path(os.environ.get("TMPDIR") or "/tmp")
    stale = markers / f"docket-branch-{session}"
    claim = markers / f"docket-claim-{session}"
    if stale.exists() and claim.exists():
        return ""

    # `docket` resolves the store from the working directory, so every command
    # runs in the checkout, never where the hook was started.
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}

    def run(command: list[str]) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(command, cwd=root, env=env, capture_output=True, check=False)

    if event != "PreToolUse" and not run(["git", "status", "--porcelain"]).stdout.strip():
        return ""

    context: list[str] = []
    if not stale.exists() and _create(stale):
        branch = run([str(docket), "branch", "--brief", "--if-stale"])
        if branch.returncode == 0:
            if branch.stdout.strip():
                context.append(_text(branch.stdout).rstrip("\n"))
        else:
            errors = _text(branch.stderr).split("\n")
            floor = [line for line in errors if line.startswith(FLOOR_REFUSAL)]
            context.append(floor[0] if floor else _failed("whether the base has moved", branch))

    check = root / "tools" / "branch_id_check.py"
    if not claim.exists() and check.is_file():
        hint: subprocess.CompletedProcess[bytes] | None = None
        if event != "PreToolUse":
            hint = run(["python3", str(check), "--hint-changed"])
        else:
            target = _edited_path(fields)
            if target:
                hint = run(["python3", str(check), "--hint", target])
        # `NOT_ASKED` is the exit status of `--hint` and `--hint-changed` where
        # nothing was asked, so the question waits for the next edit or Bash
        # call. It is imported here, after the check has run, because the file
        # starts docket, which the spent-marker path above must not pay for.
        from branch_id_check import NOT_ASKED

        if hint is not None and hint.returncode != NOT_ASKED and _create(claim):
            if hint.returncode == 0:
                if hint.stdout.strip():
                    context.append(_text(hint.stdout).rstrip("\n"))
            else:
                context.append(_failed("whether this branch claims an item", hint))

    if not context:
        return ""
    # Plain stdout from a `PreToolUse` hook reaches the debug log and nowhere
    # the session can read, so the line travels as `additionalContext`, in the
    # documented JSON form that names the event it answers.
    note = {"hookEventName": event, "additionalContext": "\n".join(context)}
    return json.dumps({"hookSpecificOutput": note})
