"""Tests for `.claude/hooks/floor-interpreter-guard.sh`, the bare-interpreter refusal.

Two interpreters are in play in this repository and both halves are deliberate.
`src/` and `tests/` target 3.14; `tools/`, `.claude/hooks/` and `bin/docket`
run under whatever bare `python3` is on PATH, which `tools/ruff.toml` pins at
the 3.11 floor `subprojects/docket/pyproject.toml` declares, so that a hook and
a bare checkout need no virtualenv.

`src/anesthesia_sim/app_metadata.py` uses PEP 758's unparenthesised `except`,
which 3.14 added and 3.11 cannot parse. So a floor parse of `src/` reports a
SyntaxError in code that is correct, and sessions and exploration subagents
kept reporting that as a defect on `main` and spending a round disproving it
(`PL-JQJQ`).

The refusal, rather than prose, is what reaches a subagent: hooks configured in
settings files fire inside subagents, and `permissionDecisionReason` is shown
to the model. So the tests that matter are about what it refuses and - more
delicately - what it lets through. A guard on a command string is one
over-broad pattern away from blocking `make check`'s own bare invocations, and
`uv run python`, an interpreter named by path, and a tool run at the floor on
purpose all have to survive it.

Nothing here runs an interpreter against the tree. The hook decides on the
command text alone.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "floor-interpreter-guard.sh"
SETTINGS = REPO / ".claude" / "settings.json"
TRIGGER = REPO / "src" / "anesthesia_sim" / "app_metadata.py"


def _decision(command: str, *, tool: str = "Bash") -> dict[str, str] | None:
    """The hook's `hookSpecificOutput` for one tool call, or `None` if it stayed quiet."""
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}})
    result = subprocess.run(
        ["bash", str(HOOK)], input=payload, capture_output=True, text=True, timeout=20
    )
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)["hookSpecificOutput"]


FLOOR_PARSE = (
    "python3 -m compileall src/",
    "python3 -m compileall -q src/",
    "python -m py_compile src/anesthesia_sim/app_metadata.py",
    "python3 src/anesthesia_sim/app_metadata.py",
    # The shape a sweep agent reaches for, and the reason the hook tokenises
    # with shlex rather than splitting on `;`: here the `;` is inside a quoted
    # argument and the path is only visible if the quoting is respected.
    "python3 -c \"import ast; ast.parse(open('src/app.py').read())\"",
    "python3 -m pytest tests/unit/test_app_metadata.py",
    "cd /home/user/open-anesthesia-sim && python3 -m compileall src/",
    "PYTHONPATH=. python3 -m compileall src/",
    # Reaches both trees without naming either.
    "python3 -m compileall .",
    # An explicit minor version is still a PATH lookup, so it is still the floor.
    "python3.11 -m compileall src/",
)


@pytest.mark.parametrize("command", FLOOR_PARSE)
def test_a_floor_parse_of_the_3_14_trees_is_denied(command: str) -> None:
    """Every spelling that points the bare interpreter at 3.14 source is refused."""
    decision = _decision(command)
    assert decision is not None, f"{command!r} was allowed"
    assert decision["permissionDecision"] == "deny"
    assert decision["hookEventName"] == "PreToolUse"


ALLOWED = (
    # The correct invocation, which is what the refusal steers towards.
    "uv run python -m compileall src/",
    "uv run pytest tests/unit/test_app_metadata.py",
    ".venv/bin/python -m compileall src/",
    # `make check` and the CI floor section run these bare on purpose; the
    # floor promise is exactly that they keep working this way.
    "python3 tools/doc_check.py check",
    "python3 tools/branch_id_check.py",
    "python3 -m compileall tools/",
    # Named by path, which is how the floor failure is reproduced deliberately.
    "/usr/bin/python3.11 -m compileall src/",
    # A guarded path in a neighbouring command convicts nothing.
    "rg -l . src/ | head",
    "git status src/",
    "grep -rn src/ docs/",
    "uv run pytest -n $(python3 -c 'import os; print(os.cpu_count() * 2)')",
    "make check",
    "python3 -c 'print(1)'",
)


@pytest.mark.parametrize("command", ALLOWED)
def test_a_correct_invocation_is_left_alone(command: str) -> None:
    """The guard is narrow: nothing here is a floor parse of 3.14 source."""
    assert _decision(command) is None, f"{command!r} was denied"


def test_prose_about_the_rule_in_a_heredoc_is_not_matched() -> None:
    """The repository documents this rule by writing the refused command down."""
    command = "cat > docs/note.md <<'EOF'\npython3 -m compileall src/\nEOF"
    assert _decision(command) is None


def test_a_non_bash_tool_is_ignored() -> None:
    """The hook is wired on Bash; anything else is not its business."""
    assert _decision("python3 -m compileall src/", tool="Read") is None


def test_the_refusal_answers_the_question_the_caller_had() -> None:
    """A denial that only says no leaves the session to investigate anyway."""
    reason = _decision("python3 -m compileall src/")["permissionDecisionReason"]
    assert "PEP 758" in reason
    assert "uv run python" in reason
    assert "PL-JQJQ" in reason
    # The refusal has to close the wrong fix as well as open the right one:
    # changing the interpreter on PATH would delete the floor guarantee.
    assert "Do not" in reason and "interpreter on PATH" in reason
    # And leave the deliberate reproduction available.
    assert "/usr/bin/python3.11" in reason


def test_the_file_the_refusal_names_still_carries_the_construct() -> None:
    """The message names a file and a construct, so both have to stay true.

    A guard whose explanation has gone stale is worse than none: it is read as
    authoritative at the moment a session has decided to trust it rather than
    look. If this assertion fails, the construct has moved or been
    parenthesized and the reason text in the hook needs rewriting - or, if
    nothing under `src/` uses 3.14-only syntax any more, the hook has stopped
    earning its place and should be retired rather than repaired.
    """
    assert "except OSError, subprocess.SubprocessError:" in TRIGGER.read_text()


def test_the_hook_is_wired_under_the_bash_matcher() -> None:
    """An unwired hook passes every test above and refuses nothing in practice."""
    hooks = json.loads(SETTINGS.read_text())["hooks"]["PreToolUse"]
    commands = [
        hook["command"]
        for entry in hooks
        if entry.get("matcher") == "Bash"
        for hook in entry["hooks"]
    ]
    assert any("floor-interpreter-guard.sh" in command for command in commands)
