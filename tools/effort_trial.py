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

**A Projects thread writes its cap into the user settings.** Claude Code
sets `CLAUDE_CODE_ENTRYPOINT=remote_projects` in a Projects thread. A thread
reads only the user and launcher settings, so it never reads
`.claude/settings.local.json` (`PL-CR81`, `PL-6LVZ`). It does read
`~/.claude/settings.json` and reloads it when it changes. A `maxEffortLevel`
written there on 2026-11-24 lowered a thread's `CLAUDE_EFFORT` from `high` to
`medium` on its next tool call, and the same key in
`.claude/settings.local.json` changed nothing (`PL-C38D`). Claude Code accepts
the key in any settings file (*Settings reference*, section
"`maxEffortLevel`", https://code.claude.com/docs/en/settings-reference, read
2026-11-24). A thread's container belongs to that thread alone, so the write
reaches no other session. So in a thread the script writes the same cap into
the user settings, and keeps every other key there, the copied hooks
included.

A cap only lowers a level. A thread drawn `xhigh` runs at `xhigh` only when it
was started at `xhigh` or above, which the project's thread effort setting
decides, so the line printed in a thread says so. Threads joined the trial on
2026-11-24. Before then each thread printed that it was in neither arm, and
before 2026-11-03 it printed an arm it never ran at, so the review treats every
thread created before `THREADS_JOIN` as in neither arm (`PL-6LVZ`).

**A session moved to another level by hand stays in the arm it drew.** The
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
a fresh draw. The model review counts a session with a moved line in the arm
it drew, because the draw is what was randomized, and reports it apart as well
(project owner, 2026-11-24, ratified, over leaving it out of both arms,
`PL-JT1C`).

**The printed line is where each arm is first written, and
`docs/effort-trial-arms.tsv` keeps it.** The digest is stored in the session's
transcript as a hook event, and a move's line as the output of the command
that made it. The harness keeps a transcript only as long as it keeps the
session, and reading one takes a call per page per session, so the model
review reads each session once and keeps what it found (`PL-JYC2`). It runs
`python3 tools/effort_trial.py pending`, which prints the ledger's sessions
that have no row in the record yet, and saves each one's events to files. Then
`python3 tools/effort_trial.py record SESSION FILE...` reads the lines from
those files with `read_lines`, the parser kept beside the functions that write
the lines, and appends the session's row. A later review reads only the
sessions that are new since. A working session writes nothing about itself,
as the ledger's design requires (`PL-92ZN`).

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
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".claude" / "hooks"))

from hook_input import PROJECTS_ENTRYPOINT, write_atomically

TRIAL_START = datetime(2026, 10, 24, 4, 0, tzinfo=UTC)
#: The day Projects threads joined the trial (`PL-C38D`). A thread created
#: earlier is in neither arm, whatever its digest says, and is never read.
THREADS_JOIN = datetime(2026, 11, 24, 0, 0, tzinfo=UTC)
ARMS = ("high", "xhigh")
#: The effort levels Claude Code accepts, lowest first. A move may name any.
LEVELS = ("low", "medium", "high", "xhigh", "max")
ROOT = Path(__file__).resolve().parent.parent
#: Where a cloud session's cap is written. A Projects thread never reads it.
SETTINGS_PATH = ROOT / ".claude" / "settings.local.json"
#: Where a Projects thread's cap is written: its user settings, which it reads.
USER_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
#: The session ledger, which names every session the review counts.
LEDGER_PATH = ROOT / "docs" / "session-ledger.tsv"
#: The record of each session's arm, written once by the model review.
ARMS_PATH = ROOT / "docs" / "effort-trial-arms.tsv"
ARMS_COLUMNS = ("session_id", "arm", "moved_to", "recorded_on")
#: The ledger's `origin` for a Projects thread.
THREAD_ORIGIN = "claude-in-hearth"
#: The settings key that records the session the cap was written for, the arm
#: it drew, the level it runs at, and why that level differs from the draw.
RECORD_KEY = "effortTrial"


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


def settings_for(thread: bool) -> Path:
    """Return the settings file this session reads its cap from.

    A Projects thread reads its user settings and never the repository's local
    settings, so its cap is written there (`PL-C38D`).
    """
    return USER_SETTINGS_PATH if thread else SETTINGS_PATH


def write_level(settings_path: Path, record: Mapping[str, str | None]) -> None:
    """Set `effortLevel` and `maxEffortLevel` to the record's level, and store the record.

    Every other key in the file is kept. The file is replaced in one step,
    because in a thread it also holds the hooks that Claude Code reloads while
    the session runs, and a half-written file would lose them.
    """
    settings = read_settings(settings_path)
    settings["effortLevel"] = record["level"]
    settings["maxEffortLevel"] = record["level"]
    settings[RECORD_KEY] = dict(record)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    write_atomically(settings_path, json.dumps(settings, indent=2) + "\n")


def write_arm(settings_path: Path, session_id: str, arm: str) -> None:
    """Set the cap to the drawn arm, and record that the draw set it."""
    write_level(
        settings_path, {"session_id": session_id, "drawn": arm, "level": arm, "reason": None}
    )


#: How every line this script prints about a session's arm begins.
LINE_START = "Effort trial: this session "


def arm_line(arm: str, thread: bool = False) -> str:
    """Return the digest line for a session in `arm`, in a cloud session or a Projects thread."""
    if thread:
        return (
            f"{LINE_START}is in the {arm} arm. The session-start hook capped its effort at "
            f"{arm} in the user settings, which a Projects thread reads. A cap only lowers a "
            f"level, so the thread runs at {arm} only if it was started at {arm} or above, "
            "which the project's thread effort setting decides."
        )
    return (
        f"{LINE_START}is in the {arm} arm. The session-start hook capped "
        f"its effort at {arm}, so it runs at {arm} unless the app's effort picker is set "
        "lower."
    )


def no_arm_line(reason: str) -> str:
    """Return the digest line for a cloud session that is in neither arm, and why."""
    return (
        f"{LINE_START}is in neither arm, because {reason}. The hook set "
        "no effort cap, so the session runs at the level it was started with, and the "
        "trial's review leaves it out."
    )


def moved_line(drawn: str, level: str, reason: str) -> str:
    """Return the line for a session moved from its drawn arm to `level`, and why."""
    return (
        f"{LINE_START}drew the {drawn} arm and was then moved to {level} "
        f"by hand, because {reason}. Its effort is capped at {level} for the rest of the "
        f"session. The trial's review still counts it in the {drawn} arm and also reports "
        "it apart. Tell the owner this in your next reply."
    )


# regex: the fixed opening of the three lines above, with the arm and the level
# they name. The arm and level alternatives come from `ARMS` and `LEVELS`, so a
# line naming anything else is not read as an arm.
LINE_RE = re.compile(
    re.escape(LINE_START)
    + "(?:is in the (?P<arm>{arms}) arm\\.|drew the (?P<drawn>{arms}) arm and was then moved "
    "to (?P<level>{levels}) |(?P<neither>is in neither arm))".format(
        arms="|".join(ARMS), levels="|".join(LEVELS)
    )
)


@dataclass(frozen=True)
class ArmReading:
    """What a session's saved events say about its arm.

    `arm` is the arm the first arm-naming line gives, `"none"` where the only
    lines say the session is in neither arm, and `None` where there is no line
    at all. `moved_to` is the level the last move line names, or "". `differs`
    counts the later arm-naming lines that name another arm, which the review
    reports (`.claude/skills/model-review/SKILL.md`, effort monitoring step 6).
    """

    arm: str | None
    moved_to: str
    differs: int


def read_lines(text: str) -> ArmReading:
    """Read the arm from the "Effort trial:" lines in `text`, in the order they appear."""
    arms: list[str] = []
    moved_to = ""
    neither = False
    for match in LINE_RE.finditer(text):
        if match["neither"]:
            neither = True
        elif match["arm"]:
            arms.append(match["arm"])
        else:
            arms.append(match["drawn"])
            moved_to = match["level"]
    if arms:
        return ArmReading(arms[0], moved_to, sum(arm != arms[0] for arm in arms))
    return ArmReading("none" if neither else None, moved_to, 0)


def _read_table(path: Path, needed: tuple[str, ...]) -> list[dict[str, str]]:
    """Return the rows of the tab-separated file at `path`, or raise `ValueError` saying why not.

    The file is split on tabs and newlines alone, as `docket.sessions` reads the
    ledger, because titles hold double quotes that no writer escaped.
    """
    lines = path.read_text(encoding="utf-8").split("\n")
    header = lines[0].split("\t")
    missing = [name for name in needed if name not in header]
    if missing:
        raise ValueError(f"{path.name} has no {', '.join(missing)} column")
    return [dict(zip(header, line.split("\t"), strict=False)) for line in lines[1:] if line.strip()]


def recorded(arms_path: Path) -> dict[str, dict[str, str]]:
    """Return the arms record by session id, or an empty one where there is no record yet."""
    if not arms_path.exists():
        return {}
    return {row["session_id"]: row for row in _read_table(arms_path, ARMS_COLUMNS)}


def pending(ledger_path: Path, arms_path: Path) -> list[str]:
    """Return the ledger's trial sessions that have no row in the arms record, oldest first.

    A session created before the trial start is not in it. Nor is a Projects
    thread created before `THREADS_JOIN`, which is in neither arm by rule.
    """
    done = recorded(arms_path)
    rows = _read_table(ledger_path, ("session_id", "created_at", "origin"))
    due: list[tuple[datetime, str]] = []
    for row in rows:
        created = datetime.fromisoformat(row["created_at"])
        if created < TRIAL_START or row["session_id"] in done:
            continue
        if row["origin"] == THREAD_ORIGIN and created < THREADS_JOIN:
            continue
        due.append((created, row["session_id"]))
    return [session_id for _, session_id in sorted(due)]


def record(
    session_id: str, texts: list[str], arms_path: Path, today: str, none: bool = False
) -> tuple[int, str]:
    """Append `session_id`'s arm, read from `texts`, to the arms record.

    Return an exit status and the line to print. `none` records a session whose
    events hold no "Effort trial:" line as in neither arm, which the review does
    only once it has checked that every page of the events was saved. A session
    already recorded is refused, so a row once written is never changed.
    """
    if not session_id.startswith("session_"):
        return 1, f"effort_trial: {session_id!r} is not a ledger session id (session_...)"
    if session_id in recorded(arms_path):
        return 1, f"effort_trial: {session_id} already has a row in {arms_path.name}"
    reading = read_lines("\n".join(texts))
    arm = reading.arm
    if arm is None:
        if not none:
            return 1, (
                f'effort_trial: the events given for {session_id} hold no "Effort trial:" '
                "line. Check that every page was saved, then record it with --none."
            )
        arm = "none"
    if not arms_path.exists():
        arms_path.parent.mkdir(parents=True, exist_ok=True)
        arms_path.write_text("\t".join(ARMS_COLUMNS) + "\n", encoding="utf-8")
    text = arms_path.read_text(encoding="utf-8")
    row = "\t".join((session_id, arm, reading.moved_to, today))
    write_atomically(arms_path, text + row + "\n")
    said = f"{session_id}: {arm}" + (f", moved to {reading.moved_to}" if reading.moved_to else "")
    if reading.differs:
        said += f"; {reading.differs} later line(s) name another arm, so report it"
    return 0, said


def session_start(
    now: datetime,
    hook_input: str,
    remote: bool,
    settings_path: Path | None = None,
    thread: bool = False,
) -> str:
    """Write this session's effort cap, and return the line that reports it.

    The cap is the drawn arm, or the level a move recorded for this same
    session. Return "" before the trial start and outside a cloud session,
    where nothing is written. `hook_input` is the JSON Claude Code gives the
    `SessionStart` hook, `remote` is whether `CLAUDE_CODE_REMOTE` is `true`,
    and `thread` is whether `CLAUDE_CODE_ENTRYPOINT` is `remote_projects`.
    `settings_path` defaults to the file `settings_for` names.
    """
    if now < TRIAL_START or not remote:
        return ""
    path = settings_path if settings_path is not None else settings_for(thread)
    session_id = hook_session_id(hook_input)
    if session_id is None:
        return no_arm_line("the session-start hook was given no session id to draw the arm from")
    arm = arm_for(session_id)
    try:
        moved = moved_record(read_settings(path), session_id)
        if moved is not None:
            write_level(path, moved)
            return moved_line(arm, moved["level"], moved["reason"])
        write_arm(path, session_id, arm)
    except (OSError, ValueError) as error:
        return no_arm_line(f"the session-start hook could not write the effort cap ({error})")
    return arm_line(arm, thread)


def move(
    level: str,
    reason: str,
    session_id: str | None,
    remote: bool,
    settings_path: Path | None = None,
    thread: bool = False,
) -> tuple[int, str]:
    """Cap this session at `level`, record why, and return an exit status and the line to print.

    The status is 0 when the move was recorded, and when there is no trial cap
    to move outside a cloud session, where nothing is written and the line says
    why. It is 1 when the move was refused, and nothing was written. A move in
    a Projects thread writes its user settings, as the draw did.
    """
    if not remote:
        return (
            0,
            "Effort trial: this is not a cloud session, so it is not in the trial, and "
            "nothing was written.",
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
        write_level(settings_path if settings_path is not None else settings_for(thread), record)
    except (OSError, ValueError) as error:
        return 1, f"effort_trial: could not write the effort cap ({error})"
    return 0, moved_line(drawn, level, reason.strip())


def main(argv: list[str]) -> int:
    """Run `session-start`, `move`, `pending` or `record`, and return the exit status."""
    remote = os.environ.get("CLAUDE_CODE_REMOTE") == "true"
    thread = os.environ.get("CLAUDE_CODE_ENTRYPOINT") == PROJECTS_ENTRYPOINT
    if argv == ["session-start"]:
        line = session_start(datetime.now(UTC), sys.stdin.read(), remote, thread=thread)
        if line:
            print(line)
        return 0
    if argv == ["pending"]:
        try:
            due = pending(LEDGER_PATH, ARMS_PATH)
        except (OSError, ValueError) as error:
            print(
                f"effort_trial: could not read the ledger or the arms record ({error})",
                file=sys.stderr,
            )
            return 1
        print("\n".join(due) if due else "effort_trial: every trial session has a recorded arm")
        return 0
    if argv[:1] == ["record"]:
        parser = argparse.ArgumentParser(prog="effort_trial.py record")
        parser.add_argument("session", help="the ledger's session id, session_...")
        parser.add_argument("files", nargs="*", type=Path, help="the session's saved events")
        parser.add_argument("--none", action="store_true", help="record no line as neither arm")
        args = parser.parse_args(argv[1:])
        try:
            texts = [path.read_text(encoding="utf-8", errors="replace") for path in args.files]
            status, line = record(
                args.session, texts, ARMS_PATH, datetime.now(UTC).date().isoformat(), args.none
            )
        except (OSError, ValueError) as error:
            status, line = 1, f"effort_trial: could not record the arm ({error})"
        print(line, file=sys.stderr if status else sys.stdout)
        return status
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
    if sys.argv[1:2] in (["session-start"], ["move"], ["pending"], ["record"]):
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
