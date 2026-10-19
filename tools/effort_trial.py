"""Assign this cloud session's effort level for the owner's effort trial.

The project owner chose a randomized trial of Claude's effort level on
2026-10-19. About one cloud session in four runs at `xhigh` and the rest at
`high`, from Friday 2026-10-23 at 11 pm CDT (2026-10-24 04:00 UTC).
`PL-HYRM` holds the measurements behind the design, and `PL-63CB`
§ "Effort monitoring" analyzes the result.

**`assign` draws the arm.** The cloud environment's setup script runs
`python3 tools/effort_trial.py` after the repository is cloned and before
Claude starts. It draws `xhigh` with probability 1/4 using `secrets`. From the
start time it writes the arm into `.claude/settings.local.json`, which git
ignores, as both `effortLevel` and `maxEffortLevel`. `effortLevel` alone loses
to the app's effort picker, which counts as an explicit choice.
`maxEffortLevel` caps every source of level, the picker included, so the arm
holds whatever the picker shows (measured in `PL-HYRM` § "The cap route,
measured"). Every run appends one tab-separated line to `/tmp/effort-trial.log`
with the time, the arm and what it did, before the start time too.

**Why the draw is random rather than a hash of the session id.** A hash would
let the model review recompute every arm from the ledger. But the setup script
runs in a container built before any session claims it, so it never sees the
session id (measured 2026-10-19, `PL-HYRM`).

**`digest` records the arm.** The `SessionStart` hook runs
`python3 tools/effort_trial.py digest`, which prints the arm in the
session-start digest. The digest is stored in the session's transcript as a
hook event, so the model review reads each session's arm from there by session
id. A container rebuilt for a resumed session draws again, so the review uses
the first arm a session's transcript shows.

**What it refuses.** An existing `.claude/settings.local.json` that is not a
JSON object is left alone: `assign` logs the failure and exits 1 rather than
overwrite settings it cannot read, and `digest` then reports no arm. The
setup-script line ends in `|| true`, so a failure here never stops a session
from starting.
"""

from __future__ import annotations

import json
import os
import secrets
import sys
from datetime import UTC, datetime
from pathlib import Path

TRIAL_START = datetime(2026, 10, 24, 4, 0, tzinfo=UTC)
ARMS = ("high", "xhigh")
LOG_PATH = Path("/tmp/effort-trial.log")
SETTINGS_PATH = Path(__file__).resolve().parent.parent / ".claude" / "settings.local.json"


def draw() -> str:
    """Return `xhigh` with probability 1/4 and `high` otherwise."""
    return ARMS[1] if secrets.randbelow(4) == 0 else ARMS[0]


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


def assign(
    now: datetime, arm: str, settings_path: Path = SETTINGS_PATH, log_path: Path = LOG_PATH
) -> int:
    """Write the arm once the trial has started, and log the run either way."""
    status = 0
    if now < TRIAL_START:
        action = "not-written: before the trial start"
    else:
        try:
            write_arm(settings_path, arm)
            action = f"written to {settings_path}"
        except (OSError, ValueError) as error:
            action = f"not-written: {error}"
            status = 1
    with log_path.open("a", encoding="utf-8") as log:
        log.write("\t".join([now.isoformat(timespec="seconds"), arm, action]) + "\n")
    if status:
        print(f"effort_trial: {action}", file=sys.stderr)
    return status


def digest_line(now: datetime, running: str, settings_path: Path = SETTINGS_PATH) -> str:
    """Return the session-start line naming this session's arm, or "" before the start.

    `running` is the level Claude Code reports in `CLAUDE_EFFORT`, or "" where
    the hook's environment does not hold it. The review analyzes the arm and
    reports the level a session actually ran at beside it.
    """
    if now < TRIAL_START:
        return ""
    ran = f" Claude Code reports it running at {running}." if running else ""
    try:
        arm = read_settings(settings_path).get("maxEffortLevel")
    except (OSError, ValueError) as error:
        arm, reason = None, str(error)
    else:
        reason = f"{settings_path} sets no maxEffortLevel"
    if arm not in ARMS:
        return (
            f"Effort trial arm: none ({reason}; {LOG_PATH} says what the setup script did). "
            "This session runs at the level the app's picker sets, and the model review "
            f"leaves it out.{ran} Tell the owner this in your first reply."
        )
    return (
        f"Effort trial arm: {arm}. The setup script capped this session at {arm}, "
        f"whatever the app's effort picker shows.{ran} Tell the owner this arm in your first reply."
    )


if __name__ == "__main__":
    if sys.argv[1:] == ["digest"]:
        line = digest_line(datetime.now(UTC), os.environ.get("CLAUDE_EFFORT", ""))
        if line:
            print(line)
        sys.exit(0)
    sys.exit(assign(datetime.now(UTC), draw()))
