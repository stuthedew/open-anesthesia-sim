"""Say so, at the first edit, if the base has moved.

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

**After a Bash call, it reads the tree rather than the command** (`PL-RXFK`).
A session can edit through Bash, which the harness's auto mode recommends for
small edits, and a Bash command names no path. So the hook also runs after
each Bash call: as `PostToolUse`, or as `PostToolUseFailure` where the
command failed, which is common when one command edits and then runs a check.
A clean tree means the call edited nothing yet, and the hook stops there. A
command that edits and commits in one call leaves a clean tree, so the
question is asked at the next call that leaves a change. Speaking just after
the edit rather than just before it costs nothing, because the hook adds
context and blocks nothing.

**Only the run that creates the marker speaks.** The hooks for parallel tool
calls run at the same time, so the marker is created with `O_EXCL`, which
refuses a file that already exists. Without it, two parallel calls could both
fetch and both print. `GIT_OPTIONAL_LOCKS=0` keeps the hook's reads of the
tree from refreshing the index as a side effect, so they never hold the index
lock while a `git add` or `git commit` in a parallel call needs it.

**A question it could not ask is said, once** (`PL-9KSJ`). A checkout with no
`bin/docket` has nothing to ask, and a tree git cannot read is taken for one
the call left clean, so each says nothing. A `bin/docket branch` that fails
spends the marker, as a question that was asked does, and the note says how
it failed.

**It asked a second question until 2026-11-21** (`PL-HS2T`): whether the
branch claimed an item, at the first edit outside the queue. The answer came
from `tools/branch_id_check.py`, which the project owner retired with its CI
refusal. `bin/docket flight` still lists a branch with work and no claim as
`unclaimed:`.
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


def decide(payload: str) -> str:
    """The note to add before an edit or after a Bash call, or "" where there is none."""
    root = hook_input.project_root()
    docket = root / "bin" / "docket"
    if not os.access(docket, os.X_OK):
        return ""
    # The id and the event are read as JSON as the rest of the payload is, so
    # an id laid out on the line after its key is still the id (`PL-CXK6`). A
    # payload that is not JSON or names no id shares the marker kept for
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
    if stale.exists():
        return ""

    # `docket` resolves the store from the working directory, so every command
    # runs in the checkout, never where the hook was started.
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}

    def run(command: list[str]) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(command, cwd=root, env=env, capture_output=True, check=False)

    if event != "PreToolUse" and not run(["git", "status", "--porcelain"]).stdout.strip():
        return ""

    context: list[str] = []
    if _create(stale):
        branch = run([str(docket), "branch", "--brief", "--if-stale"])
        if branch.returncode == 0:
            if branch.stdout.strip():
                context.append(_text(branch.stdout).rstrip("\n"))
        else:
            errors = _text(branch.stderr).split("\n")
            floor = [line for line in errors if line.startswith(FLOOR_REFUSAL)]
            context.append(floor[0] if floor else _failed("whether the base has moved", branch))

    if not context:
        return ""
    # Plain stdout from a `PreToolUse` hook reaches the debug log and nowhere
    # the session can read, so the line travels as `additionalContext`, in the
    # documented JSON form that names the event it answers.
    note = {"hookEventName": event, "additionalContext": "\n".join(context)}
    return json.dumps({"hookSpecificOutput": note})
