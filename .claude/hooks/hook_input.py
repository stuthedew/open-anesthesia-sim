"""What a hook reads before it decides anything: its checkout, and the Bash call it was handed.

Every hook here acts on one checkout, and the four Bash guards
(`floor-interpreter-guard.sh`, `gate-status-guard.sh`, `no-prune-guard.sh` and
`push-check-guard.sh`) each read the command out of the payload Claude Code
hands them. Each hook used to spell both itself (`PL-FB77`). The guards held
four identical copies of the payload reading. Five hooks found the checkout,
and they did not agree: with `CLAUDE_PROJECT_DIR` unset, four fell back to the
directory two levels above `.claude/hooks/`, and `docket-branch-guard.sh`
found none and exited, so it said nothing in a checkout where the others
acted. This module is the one answer. A hook written in Python imports it, and
one written in shell runs it as a script, which prints the checkout.

Standard library only, since a hook runs before any virtualenv is known.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import NamedTuple


def project_root() -> Path:
    """The checkout a hook acts on.

    `CLAUDE_PROJECT_DIR` is what Claude Code sets, and what `.claude/settings.json`
    uses to find each hook. Without it, the checkout is the one this file sits
    in, two directories down, so a hook run by hand from somewhere else still
    acts on its own clone.
    """
    declared = os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(declared) if declared else Path(__file__).resolve().parents[2]


class BashCall(NamedTuple):
    """The Bash call a `PreToolUse` or `PostToolUse` payload describes."""

    #: The command line Claude Code is about to run, or has run.
    command: str
    #: The directory the call runs in, as the payload gives it, or `None`.
    cwd: str | None


def bash_call(payload: str) -> BashCall | None:
    """The Bash call `payload`, a hook's JSON input, describes, or `None`.

    `None` where the payload is not JSON, names another tool, or carries no
    command string, since a guard fails open on each and lets the call run.
    """
    try:
        data = json.loads(payload)
    except ValueError:
        return None
    if not isinstance(data, dict) or data.get("tool_name") != "Bash":
        return None
    tool_input = data.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str):
        return None
    cwd = data.get("cwd")
    return BashCall(command, cwd if isinstance(cwd, str) else None)


if __name__ == "__main__":
    sys.stdout.write(f"{project_root()}\n")
