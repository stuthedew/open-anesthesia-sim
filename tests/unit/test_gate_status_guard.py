"""Tests for `.claude/hooks/gate-status-guard.sh`, the swallowed-exit-status refusal.

A shell pipeline reports its last stage, so `make check 2>&1 | tail -45` exits
with `tail`'s status and a red tree arrives as exit 0. `PL-2JRC` reported the
gate green on exactly that reading, and the false claim reached both the commit
message and the body of `#880`; `PL-D0W8` is the hook.

Two properties are under test and the second is the delicate one. What the hook
*refuses* is mechanical - every shape that discards a gate's status. What it
*allows* decides whether sessions keep using it: the guarded commands sit beside
`bin/docket next | head` and `git log | head` in every session, a quoted
argument routinely contains the very command being guarded, and a guard that
fires on those would be read past within a week. So the allow list here is
longer than the deny list on purpose.

Nothing in this file runs `make`, `pytest` or any other gate. The hook decides
on the command text alone.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "gate-status-guard.sh"
SETTINGS = REPO / ".claude" / "settings.json"


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


SWALLOWED = (
    # The command that caused the item, verbatim, and the spelling with no
    # spaces that a word-splitting tokenizer would have missed.
    "make check 2>&1 | tail -45",
    "make check|tail -45",
    # `tee` and `grep` succeed on any input exactly as `tail` does.
    "make check 2>&1 | tee /tmp/gate.log",
    "make doc-check 2>&1 | grep -i error",
    # Redirecting to a file keeps the status only until something else runs.
    "make check > /tmp/gate.log 2>&1; tail -45 /tmp/gate.log",
    # `$?` reads the status only while it is still the gate's - here `tail` has
    # replaced it, so the number printed is 0 whatever the gate did.
    "make check > /tmp/gate.log 2>&1; tail -45 /tmp/gate.log; echo $?",
    # After a background launch `$?` is the launch, never the gate.
    "make check & echo $?",
    # The fallback succeeds, so the failure never reaches the caller.
    "make check || true",
    # Backgrounded: the string exits before the gate has an answer.
    "make check &",
    # Every other guarded target.
    "make test 2>&1 | tail",
    "make docket | head -20",
    "make prebuild 2>&1 | tail -20",
    "make pr-title | tail",
    # `bin/docket`'s two verdict subcommands, and no others.
    "bin/docket check 2>&1 | tail -5",
    "bin/docket verify PL-D0W8 | tail",
    # The gates `make check` runs, reached directly while iterating - which is
    # where a session spends most of its runs.
    "uv run pytest -q tests/unit/test_gate_status_guard.py 2>&1 | tail -20",
    "uv run mypy 2>&1 | tail",
    "uv run ruff check --no-cache . 2>&1 | head -30",
    "python3 tools/doc_check.py check | head -40",
    "uv run python tools/glyph_check.py 2>&1 | tail",
    "python3 tools/dead_ends.py check | tail",
    # A leading `cd` or an environment assignment does not change the shape.
    "cd /tmp && make check 2>&1 | tail -3",
    "CI=1 make check 2>&1 | tail -3",
    # A subshell is still a pipeline.
    "(make check) | tail",
    # `&&` propagates a failure, but a `||` further right catches it again.
    "make check && echo ok || true",
)


@pytest.mark.parametrize("command", SWALLOWED)
def test_a_command_that_discards_a_gates_status_is_denied(command: str) -> None:
    """Every shape that loses the exit status is refused, whichever separator loses it."""
    decision = _decision(command)
    assert decision is not None, f"{command!r} was allowed"
    assert decision["permissionDecision"] == "deny"
    assert decision["hookEventName"] == "PreToolUse"


def test_a_newline_separates_two_commands_as_a_semicolon_does() -> None:
    """A two-line script hands the status to its last line, which shlex would not see.

    `shlex` discards a newline as whitespace, so without the substitution the
    hook reads both lines as one segment and finds nothing to the gate's right.
    """
    assert _decision("make check 2>&1 | tail -45\ngit status") is not None
    assert _decision("set -o pipefail\nmake check | tail\necho done") is not None


def test_pipefail_set_after_the_pipeline_does_not_count() -> None:
    """The option has to be in effect when the pipeline runs, not merely present."""
    assert _decision("make check | tail; set -o pipefail") is not None
    assert _decision("set +o pipefail; make check | tail") is not None


GROUPED = (
    # The command the item was found with, verbatim. The `set` opening the
    # group covers the pipe, and the `echo` reads the status straight after.
    "cd /r && git status -s && git stash -q && { set -o pipefail; uv run pytest -q "
    '-p no:randomly t.py -k "name" 2>&1 | tail -12; echo "exit=$?"; }; '
    "git stash pop -q && git status -s",
    # Both group spellings, with nothing after the pipe but the group's end.
    "{ set -o pipefail; uv run pytest -q t.py 2>&1 | tail -12; }",
    "( set -o pipefail; uv run pytest -q t.py 2>&1 | tail -12 )",
    "(set -o pipefail; cd sub && make check 2>&1 | tail -45)",
    "{\n  set -o pipefail\n  make check 2>&1 | tail -45\n}",
    # A brace group run on its own is this shell, so its `set` outlives it.
    "{ set -o pipefail; }; make check 2>&1 | tail -45",
    # A substitution is a subshell of its own; its `)` must not end the group.
    "( set -o pipefail; cd $(git rev-parse --show-toplevel) && make check 2>&1 | tail -45 )",
    # A group on the right of a pipe runs its `set` for its own pipes.
    "true | { set -o pipefail; make check 2>&1 | tail -45; }",
)


@pytest.mark.parametrize("command", GROUPED)
def test_pipefail_set_inside_a_group_keeps_the_status(command: str) -> None:
    """A `set` opening a group covers the pipes after it, for as long as bash says it does.

    `PL-1SFZ`: the `{` or `(` hid the `set` from `sets_pipefail`, so the first
    command here was refused while it kept the status, and the remedy the
    refusal offered was the token the command already carried.
    """
    assert _decision(command) is None, f"{command!r} was refused"


def test_the_semicolon_that_ends_a_group_hands_the_status_to_nothing() -> None:
    """A group exits with its last command's status; the separator after it decides the rest.

    The `;` a brace group needs before its `}` read as handing the status on,
    so `{ make check; }` was refused although nothing runs after the gate.
    """
    assert _decision("{ make check; }") is None
    assert _decision("( make check; )") is None
    assert _decision("set -o pipefail; { uv run pytest -q t.py 2>&1 | tail -12; }") is None
    assert "LAST stage" in _decision("{ make check; } | tail")["permissionDecisionReason"]
    assert "after the `;`" in _decision("{ make check; }; echo done")["permissionDecisionReason"]


ESCAPED = (
    # The `set` dies with its subshell, so the outer pipe runs without it.
    "(set -o pipefail; make check 2>&1) | tail -45",
    "( set -o pipefail; true ) && make check 2>&1 | tail -45",
    "(\n  set -o pipefail\n  true\n)\nmake check 2>&1 | tail -45",
    # A brace group that is piped or backgrounded is a subshell too.
    "{ set -o pipefail; make check 2>&1; } | tail -45",
    "{ set -o pipefail; } & make check 2>&1 | tail -45",
    # So is a `set` that is itself a pipeline stage.
    "set -o pipefail | cat; make check 2>&1 | tail -45",
    # The lexer glues `;)` into one token, and the `)` in it still ends the group.
    "( set -o pipefail; true;) && make check 2>&1 | tail -45",
)


@pytest.mark.parametrize("command", ESCAPED)
def test_pipefail_set_in_a_subshell_ends_with_it(command: str) -> None:
    """Crediting a `set` to everything after it would pass each of these, and each loses the status.

    The refusal says why, because a command that visibly sets `pipefail` and
    is refused anyway reads as the guard being wrong.
    """
    decision = _decision(command)
    assert decision is not None, f"{command!r} was allowed"
    assert "not in the shell that runs this pipe" in decision["permissionDecisionReason"]


def test_only_a_command_that_sets_pipefail_is_told_where_it_ended() -> None:
    """The note is true only of a command carrying the `set`, so no other refusal carries it."""
    reason = _decision("make check 2>&1 | tail -45")["permissionDecisionReason"]
    assert "does set `pipefail`" not in reason


PRESERVED = (
    # The bare gate, which is what the permissions allowlist names.
    "make check",
    "make check 2>&1",
    # The remedy the deny message recommends, in each spelling of `set`.
    "set -o pipefail; make check 2>&1 | tail -45",
    "set -euo pipefail; make check 2>&1 | tail -45",
    "set -eo pipefail && make check 2>&1 | tail -45",
    "set -o pipefail\nmake check 2>&1 | tail -45",
    "set -o pipefail; uv run pytest -q 2>&1 | tail -20",
    # The redirect-then-read form, split across two calls as the message says.
    "make check > /tmp/gate.log 2>&1",
    # `&&` short-circuits on failure, so the string still exits non-zero.
    "make check && tail -45 /tmp/gate.log",
    "make check > /tmp/gate.log 2>&1 && tail -45 /tmp/gate.log",
    # Reading `$?` straight out into the output. The guard's own first live
    # firing refused this one, which is what added the exemption: the `echo`
    # is the reader, and a printed verdict is plainer than an exit code.
    'make check > /tmp/gate.log 2>&1; echo "exit=$?"',
    "make check > /tmp/gate.log 2>&1; s=$?; tail -45 /tmp/gate.log; exit $s",
    'make check || echo "gate failed: $?"',
    # Informational `docket` subcommands are piped in almost every session.
    "bin/docket next | head -30",
    "bin/docket show PL-D0W8 | head -20",
    "bin/docket list | grep safety",
    # Ordinary reads.
    "git log --oneline | head -5",
    "ls tools/ | grep check",
    "cat tools/doc_check.py | head -40",
    # A gate on the right of a pipe keeps its own status.
    "cat /tmp/paths.txt | make check",
    # Targets that mutate or print rather than adjudicate.
    "make fix | tail",
    "make sync | tail",
    "make release VERSION=0.5.3 | tail",
    # An interpreter running something that is not a check.
    'uv run python -c "print(1)" | tail',
    "python3 tools/context_reading.py | tail",
)


@pytest.mark.parametrize("command", PRESERVED)
def test_a_command_that_keeps_the_status_is_allowed(command: str) -> None:
    """Anything whose exit status still reaches the caller passes without comment."""
    assert _decision(command) is None, f"{command!r} was refused"


QUOTED = (
    # Writing *about* the hazard is most of what landed the fix, and the `|`
    # here is inside an argument rather than between two commands.
    'git commit -m "PL-D0W8: make check | tail loses the status"',
    'grep -rn "make check" .claude/ | head -20',
    'rg "make check 2>&1 | tail" docs/ | head',
    'echo "run make check | tail" > /tmp/note.txt',
)


@pytest.mark.parametrize("command", QUOTED)
def test_the_guard_does_not_eat_its_own_documentation(command: str) -> None:
    """A guarded command quoted as text is text, which is why the hook tokenizes."""
    assert _decision(command) is None, f"{command!r} was refused"


def test_a_heredoc_body_is_document_content() -> None:
    """This repository writes the rule through heredocs; blocking that is self-defeating."""
    command = 'cat > /tmp/note.md <<"EOF"\nRun make check 2>&1 | tail -45\nEOF'
    assert _decision(command) is None


def test_only_bash_calls_are_considered() -> None:
    """The hook is registered on `Bash` and must stay silent if it is ever handed more."""
    assert _decision("make check | tail", tool="Read") is None
    assert _decision("make check | tail", tool="Edit") is None


def test_the_refusal_answers_the_question_the_caller_had() -> None:
    """A denial that only says no leaves the session to invent the safe form.

    The caller piped because the run is thousands of tokens of passing checks,
    so a refusal that reads as "do not pipe" trades a false green for a blown
    context budget and gets routed around. The remedy has to be in the message.
    """
    reason = _decision("make check 2>&1 | tail -45")["permissionDecisionReason"]
    assert "set -o pipefail; make check 2>&1 | tail -45" in reason
    assert "make check > /tmp/gate.log 2>&1" in reason
    assert 'echo "exit=$?"' in reason
    assert "PL-2JRC" in reason
    assert "keeping the session short" in reason


def test_the_refusal_names_the_separator_that_lost_the_status() -> None:
    """Four separators lose it for four different reasons, and the fix differs."""
    assert "LAST stage" in _decision("make check | tail")["permissionDecisionReason"]
    assert "after the `;`" in _decision("make check; echo hi")["permissionDecisionReason"]
    assert "backgrounded" in _decision("make check &")["permissionDecisionReason"]
    assert "fallback succeeds" in _decision("make check || true")["permissionDecisionReason"]


def test_the_refusal_names_the_gate_it_caught() -> None:
    """One message serves every guarded command, so it has to say which one fired."""
    assert "`uv run pytest`" not in _decision("uv run pytest | tail")["permissionDecisionReason"]
    assert "runs `pytest`" in _decision("uv run pytest | tail")["permissionDecisionReason"]
    assert "runs `mypy`" in _decision("uv run mypy | tail")["permissionDecisionReason"]
    assert (
        "runs `bin/docket check`"
        in _decision("bin/docket check | tail")["permissionDecisionReason"]
    )


MALFORMED = ("", "make check 2>&1 | tail -45 'unbalanced", "   ", "|||")


@pytest.mark.parametrize("command", MALFORMED)
def test_the_guard_fails_open(command: str) -> None:
    """A guard that breaks the session costs more than the round it saves."""
    _decision(command)  # the assertion is in `_decision`: exit 0, parseable or empty


def test_a_payload_the_hook_cannot_read_is_not_an_error() -> None:
    """Every error path exits 0 and says nothing, like the two guards beside it."""
    for payload in ("", "not json", json.dumps({"tool_name": "Bash"})):
        result = subprocess.run(
            ["bash", str(HOOK)], input=payload, capture_output=True, text=True, timeout=20
        )
        assert result.returncode == 0
        assert result.stdout.strip() == ""


def test_the_hook_is_wired_into_settings() -> None:
    """A hook nothing invokes is prose in a shell script."""
    hooks = json.loads(SETTINGS.read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
    commands = [
        hook["command"]
        for entry in hooks
        if entry.get("matcher") == "Bash"
        for hook in entry["hooks"]
    ]
    assert any("gate-status-guard.sh" in command for command in commands)
