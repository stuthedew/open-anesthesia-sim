"""Assign this cloud session's effort level for the owner's effort trial.

The project owner chose a randomized trial of Claude's effort level on
2026-10-19. About one cloud session in four runs at `xhigh` and the rest at
`high`, from Friday 2026-10-23 at 11 pm CDT (2026-10-24 04:00 UTC).
`PL-HYRM` holds the measurements behind the design, and `PL-63CB`
§ "Effort monitoring" analyzes the result.

**How it runs.** The cloud environment's setup script calls this script once,
after the repository is cloned and before Claude starts. The script writes the
session's arm into `.claude/settings.local.json`, which git ignores. It writes
both `effortLevel` and `maxEffortLevel`. `effortLevel` alone loses to the app's
effort picker, which counts as an explicit choice. `maxEffortLevel` caps every
source of level, the picker included, so the arm holds whatever the picker
shows (measured in `PL-HYRM` § "The cap route, measured").

**How the arm is drawn.** The arm is a fixed function of the session id, not a
stored random number. `arm_for` hashes the id with SHA-256 and assigns `xhigh`
when the first 8 hex digits, read as an integer, are below a quarter of 2^32.
The session ledger already holds every session id, so the model review
recomputes each session's arm by calling `arm_for` and nothing new is stored.
Online controlled experiments assign by a hash of the unit's id for the same
reason (Kohavi, Tang and Xu, *Trustworthy Online Controlled Experiments*,
Cambridge University Press, 2020).

The environment holds the id as `CLAUDE_CODE_REMOTE_SESSION_ID`, `cse_...`. The
ledger holds the same id as `session_...`, with the same suffix. `arm_for`
strips either prefix, so both forms give the same arm. Where the variable is
missing, the script draws with `secrets` instead and logs that this session's
arm cannot be recomputed from the ledger.

**What it records.** Every run appends one tab-separated line to
`/tmp/effort-trial.log`: the time, the id or `no-id`, the arm, whether the arm
can be recomputed, and what the script did. It writes the line before the start
time too, without touching the settings, so a test session can confirm the
setup script sees the id before the trial begins.

**What it refuses.** An existing `.claude/settings.local.json` that is not a
JSON object is left alone: the script logs the failure and exits 1 rather than
overwrite settings it cannot read. The setup-script line ends in `|| true`, so
a failure here never stops a session from starting.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import sys
from datetime import UTC, datetime
from pathlib import Path

TRIAL_START = datetime(2026, 10, 24, 4, 0, tzinfo=UTC)
ARMS = ("high", "xhigh")
SESSION_ID_VARIABLE = "CLAUDE_CODE_REMOTE_SESSION_ID"
ID_PREFIXES = ("cse_", "session_")
LOG_PATH = Path("/tmp/effort-trial.log")
SETTINGS_PATH = Path(__file__).resolve().parent.parent / ".claude" / "settings.local.json"


def arm_for(session_id: str) -> str:
    """Return the arm for a session id, in either its `cse_` or `session_` form."""
    suffix = session_id
    for prefix in ID_PREFIXES:
        if suffix.startswith(prefix):
            suffix = suffix[len(prefix) :]
            break
    if not suffix:
        raise ValueError(f"session id {session_id!r} has nothing after its prefix")
    digest = hashlib.sha256(suffix.encode("utf-8")).hexdigest()
    return "xhigh" if int(digest[:8], 16) < 2**32 // 4 else "high"


def write_arm(settings_path: Path, arm: str) -> None:
    """Set `effortLevel` and `maxEffortLevel` to the arm, keeping other keys."""
    settings: dict[str, object] = {}
    if settings_path.exists():
        loaded = json.loads(settings_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError(f"{settings_path} holds {type(loaded).__name__}, not a JSON object")
        settings = loaded
    settings["effortLevel"] = arm
    settings["maxEffortLevel"] = arm
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")


def run(
    now: datetime,
    environ: dict[str, str],
    settings_path: Path = SETTINGS_PATH,
    log_path: Path = LOG_PATH,
) -> int:
    """Draw the arm, write it once the trial has started, and log the run."""
    session_id = environ.get(SESSION_ID_VARIABLE, "")
    if session_id:
        arm = arm_for(session_id)
        recomputable = "recomputable"
    else:
        arm = ARMS[1] if secrets.randbelow(4) == 0 else ARMS[0]
        recomputable = "not-recomputable"
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
    fields = [now.isoformat(timespec="seconds"), session_id or "no-id", arm, recomputable, action]
    with log_path.open("a", encoding="utf-8") as log:
        log.write("\t".join(fields) + "\n")
    if status:
        print(f"effort_trial: {action}", file=sys.stderr)
    return status


if __name__ == "__main__":
    sys.exit(run(datetime.now(UTC), dict(os.environ)))
