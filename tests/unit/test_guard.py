"""Every guard runs through one entry point, which reports when a guard could not check a call.

Each guard used to handle its own failures. Whenever one crashed, it let the
call through unchecked and said nothing (`PL-9KSJ`). These tests check that:

- every hook that `.claude/settings.json` wires on a tool call starts at
  `guard.sh`, unless `EXEMPT` below names it with a reason;
- when a guard raises, prints something other than a hook's output, or runs
  past its deadline, the call goes through with a note naming the guard;
- when `python3` is missing or dies before deciding, `guard.sh` gives the
  same note;
- in those cases, a call that mentions a merge goes through like any other,
  because GitHub refuses a merge that bypasses `main`'s checks and no guard
  here judges one (`PL-39Y1`);
- each wiring's `timeout` covers the deadlines of its guards, and each
  guard's deadline covers the waits the guard sets for itself.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from importlib import import_module
from pathlib import Path

import guard as entry_point
import hook_input
import owner_ask_guard
import push_check_guard
import pytest

REPO = Path(__file__).resolve().parents[2]
SETTINGS = REPO / ".claude" / "settings.json"
LAUNCHER = REPO / ".claude" / "hooks" / "guard.sh"
BASH = shutil.which("bash") or "/bin/bash"

#: The start of every command that runs a group through the entry point.
ENTRY = 'bash "$CLAUDE_PROJECT_DIR/.claude/hooks/guard.sh" '

#: The hooks `.claude/settings.json` may wire without the entry point, and why.
#: A new hook that judges a tool call goes through `guard.sh` instead.
EXEMPT = {
    'bash "$CLAUDE_PROJECT_DIR/.claude/hooks/webfetch-quote-note.sh"': (
        "it prints a fixed note and runs no Python, so it has no check that can fail"
    ),
    'python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/stop_hook_patch.py"': (
        "a SessionStart hook, which judges no tool call"
    ),
    'bash "$CLAUDE_PROJECT_DIR/.claude/hooks/docket-digest.sh"': (
        "a SessionStart hook, which judges no tool call"
    ),
}

#: Where each group is wired: the event, then the tools it matches.
WIRED = {
    ("PreToolUse", "Edit|Write|MultiEdit|NotebookEdit"): "pre-edit",
    ("PreToolUse", "Bash"): "pre-bash",
    ("PreToolUse", "^mcp__.*$"): "pre-mcp",
    ("PostToolUse", "Bash"): "post-bash",
    ("PostToolUseFailure", "Bash"): "post-bash",
}

#: A call to a tool that every guard lets through when it can check it.
QUIET_CALL = json.dumps(
    {
        "hook_event_name": "PreToolUse",
        "tool_name": "mcp__hearthbot__react",
        "tool_input": {"message_id": "cmsg_1", "emoji": "eyes"},
    }
)

#: A merge, which no guard judges, because GitHub refuses one that bypasses
#: `main`'s checks.
MERGE_CALL = json.dumps(
    {
        "hook_event_name": "PreToolUse",
        "tool_name": "mcp__github__merge_pull_request",
        "tool_input": {"owner": "stuthedew", "repo": "open-anesthesia-sim", "pullNumber": 1},
    }
)

#: Every guard once, by its own name.
EVERY_GUARD = sorted(
    {guard.name: guard for group in entry_point.GROUPS.values() for guard in group}.values(),
    key=lambda guard: guard.name,
)


def _wiring() -> list[tuple[str, str, str, int | None]]:
    """Each command hook in `.claude/settings.json`: event, matcher, command and timeout."""
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    found = []
    for event, entries in settings["hooks"].items():
        for entry in entries:
            for hook in entry["hooks"]:
                if hook.get("type") == "command":
                    found.append(
                        (event, entry.get("matcher", ""), hook["command"], hook.get("timeout"))
                    )
    return found


def _launch(name: str, payload: str, env: dict[str, str]) -> dict[str, str] | None:
    """What `guard.sh` decides about `payload` for the group or guard `name`."""
    result = subprocess.run(
        [BASH, str(LAUNCHER), name],
        input=payload,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return None
    decided: dict[str, str] = json.loads(result.stdout)["hookSpecificOutput"]
    return decided


def _failing_python(tmp_path: Path) -> dict[str, str]:
    """An environment whose `python3` prints one error line and exits 1 at once.

    `mktemp` and `rm` are kept, since `guard.sh` reads Python's last error line
    from a scratch file. Everything else is gone, as it may be on a broken machine.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for command in ("mktemp", "rm"):
        found = shutil.which(command)
        assert found is not None
        (bin_dir / command).symlink_to(found)
    stub = bin_dir / "python3"
    stub.write_text("#!/bin/sh\necho 'broken interpreter' >&2\nexit 1\n", encoding="utf-8")
    stub.chmod(0o755)
    return {"PATH": str(bin_dir), "HOME": str(tmp_path), "TMPDIR": str(tmp_path)}


def _crash(monkeypatch: pytest.MonkeyPatch, guard: entry_point.Guard) -> None:
    """Make `guard`'s rule raise, as a guard with a bug in it would."""

    def broken(_payload: str) -> str:
        raise RuntimeError("the rule has a bug in it")

    monkeypatch.setattr(import_module(guard.module), guard.function, broken)


def test_every_hook_on_a_tool_call_runs_through_the_entry_point() -> None:
    """A hook wired another way would bring back its own failure path (`PL-9KSJ`)."""
    for event, matcher, command, _timeout in _wiring():
        if command in EXEMPT:
            continue
        assert command.startswith(ENTRY), (
            f"{event} {matcher!r} runs {command!r}, which does not start at guard.sh. "
            "Register the guard in `GROUPS` in .claude/hooks/guard.py, or name the hook "
            "in EXEMPT with the reason it needs no failure path."
        )
        assert command[len(ENTRY) :] in entry_point.GROUPS


def test_every_exempt_hook_is_still_wired() -> None:
    """An exemption whose hook has gone would excuse the next hook given that name."""
    commands = {command for _event, _matcher, command, _timeout in _wiring()}
    assert set(EXEMPT) <= commands


def test_each_group_is_wired_where_its_guards_expect() -> None:
    wired = {
        (event, matcher): command[len(ENTRY) :]
        for event, matcher, command, _timeout in _wiring()
        if command.startswith(ENTRY)
    }
    assert wired == WIRED
    assert set(WIRED.values()) == set(entry_point.GROUPS)


def test_each_wiring_gives_its_guards_their_deadlines() -> None:
    """Claude Code drops a hook's output at its `timeout`, so the guards must finish first."""
    for event, matcher, command, timeout in _wiring():
        if command.startswith(ENTRY):
            group = command[len(ENTRY) :]
            assert timeout is not None, f"{event} {matcher!r} sets no timeout"
            assert timeout >= entry_point.budget(group), (event, matcher, group)


def test_each_deadline_covers_the_waits_its_guard_sets() -> None:
    """A deadline shorter than a guard's own wait would stop it before it could say why."""
    deadline = {guard.name: guard.deadline_s for guard in EVERY_GUARD}
    assert deadline["push-check-guard"] > push_check_guard.DEADLINE
    assert deadline["owner_ask_guard"] > owner_ask_guard.ARM_TIMEOUT_S


@pytest.mark.parametrize("guard", EVERY_GUARD, ids=lambda guard: guard.name)
def test_every_guard_names_a_rule_that_exists(guard: entry_point.Guard) -> None:
    assert callable(getattr(import_module(guard.module), guard.function))


@pytest.mark.parametrize("guard", EVERY_GUARD, ids=lambda guard: guard.name)
def test_a_crashing_guard_says_it_did_not_check(
    guard: entry_point.Guard, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A guard that raises lets the call through, and the note names it and the error."""
    _crash(monkeypatch, guard)
    refusals, notes, _ = entry_point.judged((guard,), QUIET_CALL)
    assert refusals == []
    (note,) = notes
    assert f"The {guard.name} hook could not check this call" in note
    assert "the rule has a bug in it" in note


@pytest.mark.parametrize(("command", "refused"), [("gh pr merge 1", True), ("git status", False)])
def test_a_crashing_gh_guard_refuses_only_a_call_that_names_gh(
    command: str, refused: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A broken gh guard must not let a `gh` write through, nor block every other call."""
    (gh_guard,) = entry_point.selected("gh-write-guard") or ()
    _crash(monkeypatch, gh_guard)
    call = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    refusals, notes, _ = entry_point.judged((gh_guard,), call)
    assert bool(refusals) is refused
    assert bool(notes) is not refused
    assert "the rule has a bug in it" in (refusals or notes)[0]


def test_a_guard_that_prints_something_else_is_taken_for_one_that_crashed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (guard,) = entry_point.selected("regex-guard") or ()
    monkeypatch.setattr(import_module(guard.module), guard.function, lambda _payload: "ok")
    refusals, notes, _ = entry_point.judged((guard,), QUIET_CALL)
    assert refusals == []
    (note,) = notes
    assert "The regex-guard hook could not check this call" in note


def test_a_guard_past_its_deadline_is_stopped_and_said(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "slow_rule.py").write_text(
        "import time\n\n\ndef decide(payload):\n    time.sleep(30)\n    return ''\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    slow = entry_point.Guard("slow-guard", "slow_rule", deadline_s=1)
    refusals, notes, _ = entry_point.judged((slow,), QUIET_CALL)
    assert refusals == []
    assert notes == [entry_point.unchecked("slow-guard", "it did not finish within 1 second")]


def test_one_guard_crashing_leaves_the_others_judging(monkeypatch: pytest.MonkeyPatch) -> None:
    """A broken guard costs only its own check, and a refusal from another still refuses."""
    floor = entry_point.GROUPS["pre-bash"][0]
    _crash(monkeypatch, floor)
    call = json.dumps({"tool_name": "Bash", "tool_input": {"command": "make check | tail -5"}})
    refusals, notes, _ = entry_point.judged(entry_point.GROUPS["pre-bash"], call)
    assert len(refusals) == 1
    assert "make check" in refusals[0]
    assert [note for note in notes if floor.name in note]


def test_a_name_no_group_holds_is_said() -> None:
    decided = _launch("no-such-group", QUIET_CALL, dict(os.environ))
    assert decided is not None
    assert "permissionDecision" not in decided
    assert "no group or guard has that name" in decided["additionalContext"]


@pytest.mark.parametrize("guard", EVERY_GUARD, ids=lambda guard: guard.name)
def test_a_python_that_cannot_start_says_it_did_not_check(
    guard: entry_point.Guard, tmp_path: Path
) -> None:
    """`guard.sh` reports what `guard.py` cannot: an interpreter that fails before it runs."""
    decided = _launch(guard.name, QUIET_CALL, _failing_python(tmp_path))
    assert decided is not None
    assert "permissionDecision" not in decided
    note = decided["additionalContext"]
    assert f"No guard checked this call ({guard.name})" in note
    assert "python3 exited with status 1 (broken interpreter)" in note


def test_a_missing_python_says_it_did_not_check(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    decided = _launch("pre-bash", QUIET_CALL, {"PATH": str(empty)})
    assert decided is not None
    assert "python3 is not on the PATH" in decided["additionalContext"]


def test_a_python_whose_standard_library_will_not_load_says_so(tmp_path: Path) -> None:
    """A planted `json.py` stops `guard.py` at its first import, before any guard runs."""
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "json.py").write_text("raise ImportError('json will not load')\n", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(planted)}
    decided = _launch("pre-bash", QUIET_CALL, env)
    assert decided is not None
    assert "json will not load" in decided["additionalContext"]


def test_the_failure_note_keeps_the_event_it_answers(tmp_path: Path) -> None:
    after = json.dumps({"hook_event_name": "PostToolUse", "tool_name": "Bash"})
    decided = _launch("post-bash", after, _failing_python(tmp_path))
    assert decided is not None
    assert decided["hookEventName"] == "PostToolUse"


@pytest.mark.parametrize(
    "payload", [MERGE_CALL, '{"tool_input": {"body": "merge it"}}', "not json, but it says MERGE"]
)
def test_a_call_that_mentions_a_merge_is_let_through_when_no_guard_could_check_it(
    payload: str, tmp_path: Path
) -> None:
    """The launcher once refused these calls for the merge guard, now removed (`PL-39Y1`)."""
    assert not entry_point.judged(entry_point.GROUPS["pre-mcp"], payload).refusals
    decided = _launch("pre-mcp", payload, _failing_python(tmp_path))
    assert decided is not None
    assert "permissionDecision" not in decided


def test_a_bash_merge_is_let_through_when_no_guard_could_check_it(tmp_path: Path) -> None:
    """`git merge origin/main` is ordinary work, and no Bash guard judges merges."""
    call = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git merge origin/main"}})
    decided = _launch("pre-bash", call, _failing_python(tmp_path))
    assert decided is not None
    assert "permissionDecision" not in decided


def test_the_launcher_parses() -> None:
    """A line bash cannot parse would make it exit 2, which refuses every call it is wired on."""
    result = subprocess.run([BASH, "-n", str(LAUNCHER)], capture_output=True, check=False)
    assert result.returncode == 0, result.stderr


def test_the_entry_point_runs_on_the_python_the_hooks_use() -> None:
    """`guard.py` and every guard import with the interpreter running these tests."""
    result = subprocess.run(
        [sys.executable, str(LAUNCHER.with_name("guard.py")), "pre-mcp"],
        input=QUIET_CALL,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""


# --- a guard that rewrites the call's input (`PL-X4MD`) ------------------------


def _rule(tmp_path: Path, name: str, output: str) -> None:
    """A guard module `name` whose `decide` returns `output` for every call."""
    (tmp_path / f"{name}.py").write_text(
        f"def decide(payload):\n    return {output!r}\n", encoding="utf-8"
    )


def _rewriting(text: str) -> str:
    return hook_input.output("PreToolUse", rewrite={"text": text}, notes=[f"rewrote to {text}"])


def test_a_rewrite_goes_out_as_allow_with_the_new_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _rule(tmp_path, "rewriting_rule", _rewriting("new"))
    monkeypatch.syspath_prepend(str(tmp_path))
    found = entry_point.judged((entry_point.Guard("rewriting", "rewriting_rule"),), QUIET_CALL)
    assert found.rewrite == {"text": "new"}
    fields = json.loads(
        hook_input.output(
            "PreToolUse", refusals=found.refusals, notes=found.notes, rewrite=found.rewrite
        )
    )["hookSpecificOutput"]
    assert fields["permissionDecision"] == "allow"
    assert fields["updatedInput"] == {"text": "new"}
    assert fields["additionalContext"] == "rewrote to new"


def test_a_refusal_from_another_guard_stops_a_rewritten_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _rule(tmp_path, "rewriting_rule", _rewriting("new"))
    _rule(tmp_path, "refusing_rule", hook_input.output("PreToolUse", refusals=["no"]))
    monkeypatch.syspath_prepend(str(tmp_path))
    guards = (
        entry_point.Guard("rewriting", "rewriting_rule"),
        entry_point.Guard("refusing", "refusing_rule"),
    )
    found = entry_point.judged(guards, QUIET_CALL)
    fields = json.loads(
        hook_input.output(
            "PreToolUse", refusals=found.refusals, notes=found.notes, rewrite=found.rewrite
        )
    )["hookSpecificOutput"]
    assert fields["permissionDecision"] == "deny"
    assert "updatedInput" not in fields


def test_two_rewrites_of_one_call_send_it_unchanged_and_say_so(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Neither rewrite saw the other's, so sending either would drop the other."""
    _rule(tmp_path, "first_rule", _rewriting("one"))
    _rule(tmp_path, "second_rule", _rewriting("two"))
    monkeypatch.syspath_prepend(str(tmp_path))
    guards = (entry_point.Guard("first", "first_rule"), entry_point.Guard("second", "second_rule"))
    found = entry_point.judged(guards, QUIET_CALL)
    assert found.rewrite is None
    assert "The guards first, second each rewrote this call" in found.notes[-1]


def test_an_allow_without_a_new_input_is_read_as_a_failed_guard() -> None:
    """Only a rewrite may approve a call, so a bare `allow` is not output `output` builds."""
    bare = json.dumps(
        {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}
    )
    with pytest.raises(ValueError, match="no `updatedInput`"):
        hook_input.verdict(bare)
