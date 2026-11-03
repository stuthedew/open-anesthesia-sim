"""Run every guard wired on a tool call, and say so when one could not check it (`PL-9KSJ`).

`.claude/settings.json` wires `guard.sh` beside this file once for each set of
tools, with the name of a group in `GROUPS`: `pre-bash` before a Bash call,
for example. `guard.sh` starts this script with the call on standard input,
and this script runs each guard of the group on it in turn. So one Python
start serves every guard on a call, where each guard once started its own
(`PL-NDY5`, `PL-J22P`).

**Why one entry point.** Each guard used to write its own failure path, and
every one of them exited 0 on a crash with its error thrown away. A guard
that had broken therefore looked exactly like a guard that had checked the
call and found nothing wrong, and a session went on trusting it. Every new
guard copied the shape of the one it was modelled on (`PL-9KSJ`). Here the
failure path is written once:

- A guard that raises, or that does not finish within its `deadline_s`, lets
  the call through, and the note it leaves names the guard and the error.
- A guard whose `closed_on` says the call is one it must judge refuses the
  call instead. The merge guard is the one such guard: a merge that nothing
  judged would land on `main` unchecked (`PL-NXRJ`).
- A guard that prints something other than a hook's JSON is read as one that
  crashed.

`guard.sh` reports what this script cannot: a `python3` that is missing, or
one that dies before this script runs, such as on a broken standard library.
`tests/unit/test_guard.py` runs every guard through both halves with a
failing interpreter, and refuses any hook in `.claude/settings.json` that
does not start here, unless that test names it with a reason.

**What a guard is.** A module beside this file or under `tools/`, with a
function that takes the call's JSON as text and returns the hook output: a
refusal built by `hook_input.deny`, a note, or "" to let the call through.
The guards' outputs are merged into one: a refusal from any guard refuses
the call, and every reason and note is kept.

**A deadline is a backstop.** Claude Code cancels a hook at its `timeout` and
discards its output, so a guard still running then would let the call through
with nothing said (https://code.claude.com/docs/en/hooks § "Timeouts", read
2026-11-03). Each guard therefore gets its own deadline, and the `timeout` of
each wiring must cover the deadlines of every guard in its group, which the
test checks. A guard that waits on something slow keeps a shorter deadline of
its own, as the push guard does for its checks (`PL-DST3`).

Standard library only, since a hook runs before any virtualenv is known.
"""

from __future__ import annotations

import json
import signal
import sys
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from types import FrameType

HOOKS = Path(__file__).resolve().parent
TOOLS = HOOKS.parents[1] / "tools"
for _directory in (HOOKS, TOOLS):
    if str(_directory) not in sys.path:
        sys.path.insert(0, str(_directory))

import hook_input  # noqa: E402 - found through the path set just above


def mentions_merge(payload: str) -> bool:
    """Whether the call's text contains "merge" in any case.

    Every call the merge guard takes for a merge contains it, so no merge gets
    through unjudged, and the other MCP calls, such as a Projects thread's
    posts, are not refused with it. `guard.sh` holds the same rule for when no
    Python can run.
    """
    return "merge" in payload.lower()


#: The refusal of a call the merge guard could not judge, followed by why.
MERGE_UNJUDGED = (
    "Refused: the direct-merge-guard hook could not judge whether this call merges a pull "
    "request, and the call mentions a merge. A session merges by arming auto-merge "
    "(`enable_pr_auto_merge`) while a check is pending. Where GitHub will not arm a pull "
    "request because it is already in clean status, tell the owner it cannot be armed and "
    "that the Squash and merge is theirs, in the browser, and do not merge it another way "
    "(`docs/maintainer.md`; `PL-NXRJ`). What stopped the guard: "
)


@dataclass(frozen=True)
class Guard:
    """One guard: where its rule lives, how long it may take, and what its failure does."""

    #: The name its refusals are logged under and its notes name.
    name: str
    #: The module that holds the rule, beside this file or under `tools/`.
    module: str
    #: The function in `module` that takes the call's JSON and returns the hook output.
    function: str = "decide"
    #: Seconds the guard may take before it is stopped and the call goes through.
    deadline_s: int = 10
    #: Where this says the call must be judged, a guard that could not judge it
    #: refuses the call, giving `closed_reason` and then what stopped it.
    closed_on: Callable[[str], bool] | None = None
    closed_reason: str = ""


#: Every guard, by the group `.claude/settings.json` wires it in. A group runs
#: its guards in this order. A guard's own name also selects it alone, which is
#: how the tests run one guard through this entry point.
GROUPS: dict[str, tuple[Guard, ...]] = {
    "pre-edit": (
        # It fetches once per session, through `bin/docket branch`.
        Guard("docket-branch-guard", "docket_branch_guard", deadline_s=60),
        Guard("regex-guard", "regex_check", "screen"),
    ),
    "pre-bash": (
        Guard("floor-interpreter-guard", "floor_interpreter_guard"),
        Guard("gate-status-guard", "gate_status_guard"),
        # Past the 100 seconds the guard gives its checks (`DEADLINE`).
        Guard("push-check-guard", "push_check_guard", deadline_s=110),
    ),
    "pre-mcp": (
        # Past its two reads of GitHub, each given 15 seconds.
        Guard(
            "direct-merge-guard",
            "direct_merge_guard",
            deadline_s=40,
            closed_on=mentions_merge,
            closed_reason=MERGE_UNJUDGED,
        ),
        Guard("pr-body-email-guard", "pr_body_check"),
        # Past the 45 seconds it gives `bin/docket arm` (`ARM_TIMEOUT_S`).
        Guard("owner_ask_guard", "owner_ask_guard", deadline_s=55),
    ),
    "post-bash": (Guard("docket-branch-guard", "docket_branch_guard", deadline_s=60),),
}

#: Seconds a wiring's `timeout` allows beyond its guards' deadlines, for
#: starting Python and the imports.
START_S = 5


def budget(group: str) -> int:
    """The `timeout` in seconds that a wiring of `group` needs at least."""
    return sum(guard.deadline_s for guard in GROUPS[group]) + START_S


def selected(name: str) -> tuple[Guard, ...] | None:
    """The guards that `name`, a group or one guard's own name, selects, or None."""
    if name in GROUPS:
        return GROUPS[name]
    for guards in GROUPS.values():
        for guard in guards:
            if guard.name == name:
                return (guard,)
    return None


class TimedOut(Exception):
    """A guard ran past its deadline."""


def _stop(_signum: int, _frame: FrameType | None) -> None:
    raise TimedOut


def _error(error: BaseException) -> str:
    """The error, as the last line of its traceback gives it."""
    return "".join(traceback.format_exception_only(type(error), error)).strip()


def _verdict(guard: Guard, payload: str) -> hook_input.Verdict:
    """What `guard` decides about the call.

    Raises whatever the guard raised, `TimedOut`, or `ValueError` where it
    returned something other than a hook's output.
    """
    signal.signal(signal.SIGALRM, _stop)
    signal.setitimer(signal.ITIMER_REAL, guard.deadline_s)
    try:
        decide = getattr(import_module(guard.module), guard.function)
        output = decide(payload)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    return hook_input.verdict(output or "")


def unchecked(guard: str, why: str) -> str:
    """The note for a call that `guard` let through without checking it."""
    return f"The {guard} hook could not check this call, so it let the call through: {why}."


def judged(guards: tuple[Guard, ...], payload: str) -> tuple[list[str], list[str]]:
    """The reasons for refusing the call and the notes to add, from every guard in `guards`."""
    refusals: list[str] = []
    notes: list[str] = []
    for guard in guards:
        try:
            found = _verdict(guard, payload)
        except TimedOut:
            why = f"it did not finish within {guard.deadline_s} seconds"
        except (Exception, SystemExit) as error:
            why = _error(error)
        else:
            if found.refusal is not None:
                refusals.append(found.refusal)
            if found.note is not None:
                notes.append(found.note)
            continue
        if guard.closed_on is not None and guard.closed_on(payload):
            reason = guard.closed_reason + why + "."
            # Through `deny`, so the refusal is logged as every guard's is.
            hook_input.deny(guard.name, "unjudged", reason, payload)
            refusals.append(reason)
        else:
            notes.append(unchecked(guard.name, why))
    return refusals, notes


def main(argv: list[str]) -> int:
    """Judge the call on standard input with the guards `argv[0]` names, and print the result."""
    payload = sys.stdin.read()
    name = argv[0] if argv else ""
    try:
        call = json.loads(payload)
    except ValueError:
        call = None
    event = call.get("hook_event_name") if isinstance(call, dict) else None
    if not isinstance(event, str) or not event:
        event = "PreToolUse"
    guards = selected(name)
    if guards is None:
        refusals: list[str] = []
        notes = [unchecked(f"`{name}`", "no group or guard has that name in `guard.py`")]
    else:
        # Each guard is still run on a call it cannot read, since the merge
        # guard refuses one that mentions a merge.
        refusals, notes = judged(guards, payload)
        if not isinstance(call, dict):
            notes.append(unchecked(name, "the call it was handed is not a JSON object"))
    sys.stdout.write(hook_input.output(event, refusals=refusals, notes=notes))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
