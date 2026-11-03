"""Assign this cloud session's effort level for the owner's effort trial.

The project owner chose a randomized trial of Claude's effort level on
2026-10-19. It starts on Friday 2026-10-23 at 11 pm CDT (2026-10-24 04:00
UTC). Half of the cloud sessions run at `xhigh` and half at `high`. The split
was one session in four at `xhigh` until the owner moved it to 50/50 on
2026-10-24, because an equal split needs about a quarter fewer sessions for
the same statistical power (`PL-TN18`). `PL-HYRM` holds the measurements
behind the design, and `PL-63CB` § "Effort monitoring" analyzes the result.

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
read as a whole number, is even. That is about one session in two. Every
digest divisible by 4, the old rule, is also even, so a session already in
the `xhigh` arm stays there.
The hook runs again when a session resumes or compacts, and a hash gives the
same session the same arm each time. The draw used to run in the cloud
environment's setup script. That script runs only when the environment's
snapshot is built, about once a week, so it assigned no session an arm
(`PL-8MZ9`). Its line now does nothing and can be removed.

**Only cloud sessions are in the trial.** Claude Code sets
`CLAUDE_CODE_REMOTE=true` in a cloud container. On the owner's own computer
the script writes nothing and prints nothing, so it never caps the owner's
local sessions.

**A Projects thread is in neither arm.** Claude Code sets
`CLAUDE_CODE_ENTRYPOINT=remote_projects` in a Projects thread. A thread reads
only the user and launcher settings, so it never reads
`.claude/settings.local.json` and the cap written there does nothing. The
CLI's diagnostics log showed `source_count: 2` at every settings load in a
thread on 2026-10-26 and again on 2026-11-03, and a hook written into that
file never fired (`PL-CR81`, `PL-6LVZ`). A thread runs at the level the
project's coordinator started it with. So in a thread the script writes
nothing and prints the line that says the session is in neither arm. Until
`PL-6LVZ`, it printed an arm that the thread never ran at.

**A session moved to another level by hand is left out of both arms.** The
project owner ruled on 2026-11-02 that a session working on a generator's
cause runs at `xhigh` whatever arm it drew, and the owner can also move a
session by hand. Either way the draw no longer set the session's effort.
`python3 tools/effort_trial.py move --to xhigh --reason "<why>"` writes the
new level as the cap and records the move in the same file, under
`effortTrial`, with the session id from `CLAUDE_CODE_SESSION_ID`. That id is
the one the hook is given: the session's transcript file is named by it. The
command prints a line that says the session was moved and why. When the hook
runs again for the same session, on a resume or a compaction, it keeps the
moved level and prints the moved line again, so a compaction no longer writes
the drawn cap back over the move (`PL-WBW3`). A session with another id gets
a fresh draw. The model review leaves every session with a moved line out of
both arms.

**The printed line is the trial's record of the arm.** The digest is stored
in the session's transcript as a hook event, and the model review reads each
session's arm from there by session id. A move's line is stored there too, as
the output of the command that made it. The line also says why when a
session is in neither arm, so no separate log is kept.

**What it refuses.** An existing `.claude/settings.local.json` that is not a
JSON object is left alone, and the printed line says the session is in
neither arm and why. A hook input with no session id draws nothing, because a
random fallback would give a resumed session a new arm. The digest hook
ignores this script's exit status, so a failure here never stops a session
from starting.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".claude" / "hooks"))

from hook_input import PROJECTS_ENTRYPOINT

TRIAL_START = datetime(2026, 10, 24, 4, 0, tzinfo=UTC)
ARMS = ("high", "xhigh")
#: The effort levels Claude Code accepts, lowest first. A move may name any.
LEVELS = ("low", "medium", "high", "xhigh", "max")
SETTINGS_PATH = Path(__file__).resolve().parent.parent / ".claude" / "settings.local.json"
#: The settings key that records the session the cap was written for, the arm
#: it drew, the level it runs at, and why that level differs from the draw.
RECORD_KEY = "effortTrial"
THREAD_REASON = (
    "it is a Projects thread, which does not read the settings file where the hook "
    "writes the effort cap"
)


def arm_for(session_id: str) -> str:
    """Return `xhigh` when SHA-256 of `session_id` is even, and `high` otherwise."""
    digest = hashlib.sha256(session_id.encode("utf-8")).digest()
    return ARMS[1] if int.from_bytes(digest, "big") % 2 == 0 else ARMS[0]


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


def moved_record(settings: dict[str, object], session_id: str) -> dict[str, str] | None:
    """Return the settings' record of a move made in `session_id`, or `None` where there is none.

    A record written for another session, a record of a drawn level, and a
    record that is not well formed all return `None`, so the hook draws afresh.
    """
    record = settings.get(RECORD_KEY)
    if not isinstance(record, dict) or record.get("session_id") != session_id:
        return None
    level, reason = record.get("level"), record.get("reason")
    if level not in LEVELS or not isinstance(reason, str) or not reason:
        return None
    return {
        "session_id": session_id,
        "drawn": arm_for(session_id),
        "level": level,
        "reason": reason,
    }


def write_level(settings_path: Path, record: Mapping[str, str | None]) -> None:
    """Set `effortLevel` and `maxEffortLevel` to the record's level, and store the record.

    Every other key in the file is kept.
    """
    settings = read_settings(settings_path)
    settings["effortLevel"] = record["level"]
    settings["maxEffortLevel"] = record["level"]
    settings[RECORD_KEY] = dict(record)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")


def write_arm(settings_path: Path, session_id: str, arm: str) -> None:
    """Set the cap to the drawn arm, and record that the draw set it."""
    write_level(
        settings_path, {"session_id": session_id, "drawn": arm, "level": arm, "reason": None}
    )


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


def moved_line(drawn: str, level: str, reason: str) -> str:
    """Return the line for a session moved from its drawn arm to `level`, and why."""
    return (
        f"Effort trial: this session drew the {drawn} arm and was then moved to {level} "
        f"by hand, because {reason}. Its effort is capped at {level} for the rest of the "
        "session, and the trial's review leaves it out of both arms. Tell the owner this "
        "in your next reply."
    )


def session_start(
    now: datetime,
    hook_input: str,
    remote: bool,
    settings_path: Path = SETTINGS_PATH,
    thread: bool = False,
) -> str:
    """Write this session's effort cap, and return the line that reports it.

    The cap is the drawn arm, or the level a move recorded for this same
    session. Return "" before the trial start and outside a cloud session,
    where nothing is written. In a Projects thread nothing is written either,
    and the line says the session is in neither arm. `hook_input` is the JSON
    Claude Code gives the `SessionStart` hook, `remote` is whether
    `CLAUDE_CODE_REMOTE` is `true`, and `thread` is whether
    `CLAUDE_CODE_ENTRYPOINT` is `remote_projects`.
    """
    if now < TRIAL_START or not remote:
        return ""
    if thread:
        return no_arm_line(THREAD_REASON)
    session_id = hook_session_id(hook_input)
    if session_id is None:
        return no_arm_line("the session-start hook was given no session id to draw the arm from")
    arm = arm_for(session_id)
    try:
        moved = moved_record(read_settings(settings_path), session_id)
        if moved is not None:
            write_level(settings_path, moved)
            return moved_line(arm, moved["level"], moved["reason"])
        write_arm(settings_path, session_id, arm)
    except (OSError, ValueError) as error:
        return no_arm_line(f"the session-start hook could not write the effort cap ({error})")
    return arm_line(arm)


def move(
    level: str,
    reason: str,
    session_id: str | None,
    remote: bool,
    settings_path: Path = SETTINGS_PATH,
    thread: bool = False,
) -> tuple[int, str]:
    """Cap this session at `level`, record why, and return an exit status and the line to print.

    The status is 0 when the move was recorded, and when there is no trial
    cap to move: outside a cloud session and in a Projects thread, where
    nothing is written and the line says why. It is 1 when the move was
    refused, and nothing was written.
    """
    if not remote:
        return (
            0,
            "Effort trial: this is not a cloud session, so it is not in the trial, and "
            "nothing was written.",
        )
    if thread:
        return 0, (
            f"Effort trial: this session is in neither arm, because {THREAD_REASON}. "
            "Nothing was written. Set a thread's level with the thread's own effort setting."
        )
    if level not in LEVELS:
        return 1, f"effort_trial: {level!r} is not an effort level; use one of {', '.join(LEVELS)}"
    if not reason.strip():
        return 1, "effort_trial: give the reason for the move with --reason"
    if not session_id:
        return (
            1,
            "effort_trial: CLAUDE_CODE_SESSION_ID is not set, so the move cannot name its session",
        )
    drawn = arm_for(session_id)
    record: dict[str, str | None] = {
        "session_id": session_id,
        "drawn": drawn,
        "level": level,
        "reason": reason.strip(),
    }
    try:
        write_level(settings_path, record)
    except (OSError, ValueError) as error:
        return 1, f"effort_trial: could not write the effort cap ({error})"
    return 0, moved_line(drawn, level, reason.strip())


def main(argv: list[str]) -> int:
    """Run `session-start` or `move`, and return the exit status."""
    remote = os.environ.get("CLAUDE_CODE_REMOTE") == "true"
    thread = os.environ.get("CLAUDE_CODE_ENTRYPOINT") == PROJECTS_ENTRYPOINT
    if argv == ["session-start"]:
        line = session_start(datetime.now(UTC), sys.stdin.read(), remote, thread=thread)
        if line:
            print(line)
        return 0
    parser = argparse.ArgumentParser(prog="effort_trial.py move")
    parser.add_argument("--to", required=True, choices=LEVELS, help="the level to run at")
    parser.add_argument("--reason", required=True, help="why the level differs from the draw")
    args = parser.parse_args(argv[1:])
    status, line = move(
        args.to, args.reason, os.environ.get("CLAUDE_CODE_SESSION_ID"), remote, thread=thread
    )
    print(line, file=sys.stderr if status else sys.stdout)
    return status


if __name__ == "__main__":
    if sys.argv[1:2] in (["session-start"], ["move"]):
        sys.exit(main(sys.argv[1:]))
    # The cloud environment's setup script still runs this file with no
    # arguments until the owner removes its line. The draw moved to the
    # session-start hook, so that run does nothing.
    print(
        "effort_trial: the session-start hook draws the arm now (PL-8MZ9); "
        "this setup-script line does nothing and can be removed",
        file=sys.stderr,
    )
    sys.exit(0)
