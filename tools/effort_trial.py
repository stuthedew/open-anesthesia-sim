"""Assign this cloud session's effort level for the owner's effort trial.

The project owner chose a randomized trial of Claude's effort level on
2026-10-19. About one cloud session in four runs at `xhigh` and the rest at
`high`, from Friday 2026-10-23 at 11 pm CDT (2026-10-24 04:00 UTC).
`PL-HYRM` holds the measurements behind the design, and `PL-63CB`
§ "Effort monitoring" analyzes the result.

**The session-start hook draws the arm and reports it, in one step.**
`.claude/hooks/docket-digest.sh` runs `python3 tools/effort_trial.py
session-start` and pipes in the JSON that Claude Code gives the hook. The
script writes the arm into `.claude/settings.local.json`, which git ignores,
as both `effortLevel` and `maxEffortLevel`. Then it prints the line that
names the arm. Claude Code runs a session's hooks in parallel, so a second
hook reading the file could run before this one wrote it. Writing and
reporting in one process is what makes the line match the cap (`PL-8MZ9`).

`effortLevel` alone loses to the app's effort picker, which counts as an
explicit choice. `maxEffortLevel` caps every source of level, the picker
included (measured in `PL-HYRM` § "The cap route, measured"). Claude Code
reloads its settings when the file changes and applies the cap before each
request. A probe session measured a cap written by this hook on its first
request (`PL-8MZ9` § "Probe result").

**The arm is a hash of the hook's `session_id`, not a random draw.** The
session is in the `xhigh` arm when the SHA-256 digest of its `session_id`,
read as a whole number, is divisible by 4. That is about one session in four.
The hook runs again when a session resumes or compacts, and a hash gives the
same session the same arm each time. The draw used to run in the cloud
environment's setup script. That script runs only when the environment's
snapshot is built, about once a week, so it assigned no session an arm
(`PL-8MZ9`). Its line now does nothing and can be removed.

**Only cloud sessions are in the trial.** Claude Code sets
`CLAUDE_CODE_REMOTE=true` in a cloud container. On the owner's own computer
the script writes nothing and prints nothing, so it never caps the owner's
local sessions.

**The printed line is the trial's record of the arm.** The digest is stored
in the session's transcript as a hook event, and the model review reads each
session's arm from there by session id. The line also says why when a
session is in neither arm, so no separate log is kept.

**What it refuses.** An existing `.claude/settings.local.json` that is not a
JSON object is left alone, and the printed line says the session is in
neither arm and why. A hook input with no session id draws nothing, because a
random fallback would give a resumed session a new arm. The digest hook
ignores this script's exit status, so a failure here never stops a session
from starting.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

TRIAL_START = datetime(2026, 10, 24, 4, 0, tzinfo=UTC)
ARMS = ("high", "xhigh")
SETTINGS_PATH = Path(__file__).resolve().parent.parent / ".claude" / "settings.local.json"


def arm_for(session_id: str) -> str:
    """Return `xhigh` when SHA-256 of `session_id` is divisible by 4, and `high` otherwise."""
    digest = hashlib.sha256(session_id.encode("utf-8")).digest()
    return ARMS[1] if int.from_bytes(digest, "big") % 4 == 0 else ARMS[0]


def hook_session_id(hook_input: str) -> str | None:
    """Return the `session_id` in the hook's JSON input, or `None` where it has none."""
    try:
        payload = json.loads(hook_input)
    except ValueError:
        return None
    session_id = payload.get("session_id") if isinstance(payload, dict) else None
    return session_id if isinstance(session_id, str) and session_id else None


def read_settings(settings_path: Path) -> dict[str, object]:
    """Return the settings file's object, or an empty one where there is no file."""
    if not settings_path.exists():
        return {}
    loaded = json.loads(settings_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{settings_path} holds {type(loaded).__name__}, not a JSON object")
    return loaded


def write_arm(settings_path: Path, arm: str) -> None:
    """Set `effortLevel` and `maxEffortLevel` to the arm, keeping other keys."""
    settings = read_settings(settings_path)
    settings["effortLevel"] = arm
    settings["maxEffortLevel"] = arm
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")


def arm_line(arm: str) -> str:
    """Return the digest line for a session in `arm`."""
    return (
        f"Effort trial: this session is in the {arm} arm. The session-start hook capped "
        f"its effort at {arm}, so it runs at {arm} unless the app's effort picker is set "
        "lower. Tell the owner this in your first reply."
    )


def no_arm_line(reason: str) -> str:
    """Return the digest line for a cloud session that is in neither arm, and why."""
    return (
        f"Effort trial: this session is in neither arm, because {reason}. The hook set "
        "no effort cap, so the session runs at the level it was started with, and the "
        "trial's review leaves it out. Tell the owner this in your first reply."
    )


def session_start(
    now: datetime, hook_input: str, remote: bool, settings_path: Path = SETTINGS_PATH
) -> str:
    """Write this session's arm as its effort cap, and return the line that reports it.

    Return "" before the trial start and outside a cloud session, where
    nothing is written. `hook_input` is the JSON Claude Code gives the
    `SessionStart` hook, and `remote` is whether `CLAUDE_CODE_REMOTE` is
    `true`.
    """
    if now < TRIAL_START or not remote:
        return ""
    session_id = hook_session_id(hook_input)
    if session_id is None:
        return no_arm_line("the session-start hook was given no session id to draw the arm from")
    arm = arm_for(session_id)
    try:
        write_arm(settings_path, arm)
    except (OSError, ValueError) as error:
        return no_arm_line(f"the session-start hook could not write the effort cap ({error})")
    return arm_line(arm)


if __name__ == "__main__":
    if sys.argv[1:] == ["session-start"]:
        line = session_start(
            datetime.now(UTC), sys.stdin.read(), os.environ.get("CLAUDE_CODE_REMOTE") == "true"
        )
        if line:
            print(line)
        sys.exit(0)
    # The cloud environment's setup script still runs this file with no
    # arguments until the owner removes its line. The draw moved to the
    # session-start hook, so that run does nothing.
    print(
        "effort_trial: the session-start hook draws the arm now (PL-8MZ9); "
        "this setup-script line does nothing and can be removed",
        file=sys.stderr,
    )
    sys.exit(0)
