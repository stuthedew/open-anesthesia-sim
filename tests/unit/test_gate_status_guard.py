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
    """A two-line script hands the status to its last line.

    A reader that took the newline for whitespace would read both lines as one
    command and find nothing to the gate's right.
    """
    assert _decision("make check 2>&1 | tail -45\ngit status") is not None
    assert _decision("set -o pipefail\nmake check | tail\necho done") is not None


def test_a_newline_after_an_operator_is_a_linebreak() -> None:
    """Bash reads a newline after `&&`, `||`, `|` or `;` as a linebreak, not another `;`.

    The newline substitution read `make check &&` and a `tail` on the next line
    as the gate handing its status to the `tail`, and refused a list that keeps it.
    """
    assert _decision("make check &&\ntail -5 /tmp/gate.log") is None
    assert _decision("set -o pipefail; make check 2>&1 |\n  tail -45") is None
    assert _decision("make check 2>&1 |\n  tail -45") is not None


def test_a_comment_ends_at_its_line() -> None:
    """A `#` hides the rest of its line and nothing after it.

    The comment used to run to the end of the whole command, so a gate on any
    line after one was never read.
    """
    assert _decision("git status  # a note\nmake check 2>&1 | tail -45") is not None
    assert _decision("make check  # the | tail here is a comment") is None


def test_a_backslash_newline_continues_the_command() -> None:
    """A line ending in a backslash goes on, and separates nothing (`PL-R5RF`).

    The newline substitution turned the pair into an escaped space and a `;`,
    and read the gate as handing its status to the next line: the first command
    here was refused although `pipefail` keeps the status, by a refusal blaming
    a `;` the command does not contain.
    """
    assert (
        _decision("set -o pipefail; uv run pytest -q \\\n  tests/unit/x.py 2>&1 | tail -5") is None
    )
    # Joined, a gate piped without `pipefail` still loses its status.
    assert _decision("uv run pytest -q \\\n  tests/unit/x.py 2>&1 | tail -5") is not None
    assert _decision('make check 2>&1 \\\n  | tail -5; echo "exit=$?"') is not None


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
    # An `if` or a loop run on its own is this shell too (`PL-0X0G`).
    "if true; then set -o pipefail; fi; make check 2>&1 | tail -45",
    "for f in a; do set -o pipefail; done; make check 2>&1 | tail -45",
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
    # `;)` is two operators, and the `)` still ends the group.
    "( set -o pipefail; true;) && make check 2>&1 | tail -45",
    # A piped `if` or loop is a subshell as a piped group is (`PL-0X0G`).
    "if true; then set -o pipefail; fi | cat; make check 2>&1 | tail -45",
    "for f in a; do set -o pipefail; done | cat; make check 2>&1 | tail -45",
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


RESERVED = (
    # `PL-0X0G`'s reproductions, verbatim: the gate after `do`, `then` or `time`
    # read as a command named for the reserved word, so the pipe that loses its
    # status was never looked at.
    "for f in a; do make check | tail; done",
    "if true; then make check | tail; fi",
    "time make check | tail",
    # Every other reserved word bash reads with a command after it, and the two
    # options `time` takes before its pipeline.
    "if false; then :; elif true; then make check | tail; fi",
    "if false; then :; else make check | tail; fi",
    "while true; do uv run pytest -q 2>&1 | tail -5; break; done",
    "until make check | tail; do sleep 1; done",
    "if make check 2>&1 | tail -45; then echo green; fi",
    "time -p -- make check 2>&1 | tail",
    "! time make check | tail",
)


@pytest.mark.parametrize("command", RESERVED)
def test_a_reserved_word_opens_the_command_after_it(command: str) -> None:
    """`do`, `then`, `time` and the rest are bash's words, not the command's name (`PL-0X0G`).

    `shell_split.command_words` dropped a leading `(`, `{`, `!` and assignments
    and nothing else, so the guard read each gate here as a command named `do`
    or `time` and let the pipe lose its status.
    """
    decision = _decision(command)
    assert decision is not None, f"{command!r} was allowed"
    assert "LAST stage" in decision["permissionDecisionReason"]


WRAPPED = (
    # `PL-TRMN`'s reproduction, verbatim, and the spelling a long suite gets.
    ("timeout 600 make check | tail -5", True),
    ("timeout 600 uv run pytest -q 2>&1 | tail -5", True),
    # Each wrapper by its own grammar, named bare or by path, and nested.
    ("timeout -s KILL -k 5 900 make check | tail", True),
    ("env CI=1 make check | tail", True),
    ("/usr/bin/env -u CI make check | tail", True),
    ("nice -n 10 nohup make check &", True),
    ("command make check | tail", True),
    ("exec -a gate make check | tail", True),
    ("echo t.py | xargs -n 1 uv run pytest -q | tail", True),
    ("uv run timeout 60 pytest -q | tail", True),
    # A wrapper keeps the status wherever the bare gate keeps it.
    ("set -o pipefail; timeout 600 make check 2>&1 | tail -5", False),
    ("timeout 600 make check", False),
    ('timeout 600 make check > /tmp/gate.log 2>&1; echo "exit=$?"', False),
    # And runs no gate where it describes one, or runs something else.
    ("command -v pytest | head", False),
    ("timeout 60 bin/docket next | head -30", False),
    ("env | grep PATH", False),
)


@pytest.mark.parametrize(("command", "refused"), WRAPPED)
def test_a_wrapper_runs_the_command_after_it(command: str, refused: bool) -> None:
    """A gate run through `timeout`, `env` or another wrapper is the gate (`PL-TRMN`).

    The guard read the wrapper as the command, so each refused pipe here
    passed, while the same pipe without `timeout` was refused.
    """
    decision = _decision(command)
    assert (decision is not None) is refused, f"{command!r}: refused={decision is not None}"


REDIRECTED = (
    # `PL-K9QL`'s reproductions, verbatim: ahead of the command, and among a
    # wrapper's words.
    ("2>/dev/null make check | tail -5", True),
    ("timeout 5 >x make check | tail", True),
    # Among assignments in any order, and among the program's own words.
    ("FOO=1 2>/dev/null BAR=2 make check | tail", True),
    ("{ >/tmp/gate.log make check; } | tail", True),
    ("bin/docket 2>/dev/null check | tail -5", True),
    ("uv 2>&1 run pytest -q | tail", True),
    # A number written against the operator is its descriptor, so this hands
    # `timeout` the duration `make`, which it refuses, and runs no gate. Quoted
    # or spaced, as in the second line above, a number is a word.
    ("timeout 5>x make check | tail", False),
    ("timeout '5'>x make check | tail", True),
    # A `set` after a redirection still runs in this shell.
    ("2>/dev/null set -o pipefail; make check 2>&1 | tail -5", False),
)


@pytest.mark.parametrize(("command", "refused"), REDIRECTED)
def test_a_redirection_is_not_a_word_of_the_command(command: str, refused: bool) -> None:
    """Bash lifts a redirection out wherever it stands, so it hides no gate (`PL-K9QL`).

    The guard read `2>/dev/null` as the word `2` and took it for the command,
    or for the subcommand after `bin/docket`, and a wrapper stopped reading at
    the `>`: each refused pipe here lost its status unrefused.
    """
    decision = _decision(command)
    assert (decision is not None) is refused, f"{command!r}: refused={decision is not None}"


RUN_A_BUILTIN = (
    # `PL-9RSP`'s reproduction, verbatim, and the two spellings found beside it.
    ("command set -o pipefail; make check 2>&1 | tail -45", False),
    ("command -p set -o pipefail; make check 2>&1 | tail -45", False),
    ("builtin set -o pipefail; make check 2>&1 | tail -45", False),
    # The one option each takes, the two nested either way round, and each
    # after an assignment or around a redirection.
    ("command -p -- set -o pipefail; make check 2>&1 | tail -45", False),
    ("builtin -- set -o pipefail; make check 2>&1 | tail -45", False),
    ("command builtin set -o pipefail; make check 2>&1 | tail -45", False),
    ("builtin command set -o pipefail; make check 2>&1 | tail -45", False),
    ("FOO=1 command set -o pipefail; make check 2>&1 | tail -45", False),
    ("command 2>/dev/null set -o pipefail; make check 2>&1 | tail -45", False),
    # None of these runs `set` in this shell: `-v` describes it, `builtin`
    # refuses `-p`, and the rest look for a program and find none.
    ("command -v set; make check 2>&1 | tail -45", True),
    ("builtin -p set -o pipefail; make check 2>&1 | tail -45", True),
    ("exec set -o pipefail; make check 2>&1 | tail -45", True),
    ("timeout 5 set -o pipefail; make check 2>&1 | tail -45", True),
    ("/usr/bin/command set -o pipefail; make check 2>&1 | tail -45", True),
    # And a `set +o` run by `command` turns it off, as a bare one does.
    ("command set +o pipefail; make check 2>&1 | tail -45", True),
)


@pytest.mark.parametrize(("command", "refused"), RUN_A_BUILTIN)
def test_pipefail_set_through_command_or_builtin_keeps_the_status(
    command: str, refused: bool
) -> None:
    """`command` and `builtin` run the `set` builtin in this shell (`PL-9RSP`).

    The guard read neither, so each spelling here that bash 5.2.21 holds
    pipefail after was refused as setting nothing, while `timeout 5 set` is
    rightly refused: it looks for a program named `set`.
    """
    decision = _decision(command)
    assert (decision is not None) is refused, f"{command!r}: refused={decision is not None}"


COMPOUND = (
    # A gate ending an `if` branch leaves with the `if`, whose status is "the
    # exit status of the last command executed" (`help if`, bash 5.2.21). The
    # second was refused before `PL-0X0G`, by a `;` read as handing the status
    # to the `fi`.
    ("if true; then make check; fi", False),
    ("if true; then\n  make check\nfi", False),
    ("if true; then make check; else echo skipped; fi", False),
    ("if false; then :; elif true; then make check; else echo a; echo b; fi", False),
    ('if true; then make check; fi; echo "exit=$?"', False),
    ("if true; then make check; fi | tail", True),
    ("if true; then make check; else echo skipped; fi; git status", True),
    ("if true; then make check; echo built; fi", True),
    # A gate ending an `if`, `while` or `until` test is read by it, as `$?` is.
    ("if make check > /tmp/gate.log 2>&1; then echo green; else echo RED; fi", False),
    ("until make check; do sleep 5; done", False),
    # A gate ending a loop body is not: the next pass replaces its status, so
    # a red pass before a green one exits 0 (`help for`, `help while`).
    ("for t in a b; do uv run pytest -q $t; done", True),
    ("for t in a b; do set -o pipefail; uv run pytest -q $t 2>&1 | tail -5; done", True),
    ('for t in a b; do uv run pytest -q $t; echo "exit=$?"; done', False),
    # After `&&`, or a pipe under `pipefail`, the status travels to the end of
    # a pipeline, and an `if`, a loop or a group ends where it closes, not at
    # the first `;` inside it.
    ("make check && if true; then echo ok; fi; git status", True),
    ("make check && { echo a; echo b; }", False),
    ("set -o pipefail; make check 2>&1 | while read -r l; do echo $l; done; git status", True),
)


@pytest.mark.parametrize(("command", "refused"), COMPOUND)
def test_an_if_or_a_loop_hands_the_status_on_as_bash_runs_it(command: str, refused: bool) -> None:
    """Once the guard can see a gate inside an `if` or a loop, it has to read the construct too.

    Read as a plain `;`, every `if` branch ending in a gate would be refused
    although it keeps the status, and every loop allowed although it loses it.
    """
    decision = _decision(command)
    assert (decision is not None) is refused, f"{command!r}: refused={decision is not None}"


def test_a_loop_refusal_says_the_next_pass_replaced_the_status() -> None:
    """The `;` before `done` hands the status to another pass, not to a command the reader wrote."""
    reason = _decision("for t in a b; do uv run pytest -q $t; done")["permissionDecisionReason"]
    assert "next pass" in reason
    assert 'echo "exit=$?"; done' in reason


FALLBACKS = (
    # `PL-KQ4Q`'s reproductions: each fallback fails too, so a failing gate
    # still exits non-zero, and each was refused as one that succeeds. The
    # comment is the exit bash 5.2.21 gave with the gate failing.
    ("make check || exit 1", False),  # 1
    ("make check || exit", False),  # the gate's own, as nothing ran since the `||`
    ("make check || false", False),  # 1
    ("make check || { echo red; exit 1; }", False),  # 1
    ("for t in a b; do make check || exit 1; done", False),  # 1, before the next pass
    # The rest of the line bash draws.
    ("make check || { exit; }", False),  # the gate's own
    ("make check || (echo red; exit 1)", False),  # 1
    ("make check || { echo red; false; }", False),  # 1
    ("make check || exit 1; echo after", False),  # 1, and the `echo` never runs
    ("make check || exit -1", False),  # 255
    ("make check && echo ok || exit 1", False),  # 1
    ("( make check || exit 1 )", False),  # 1
    ("set -o pipefail; make check || exit 1 | tail -1", False),  # 1
    ("make check || { echo red; exit; }", True),  # 0, the status of the `echo`
    ("make check || exit 0", True),  # 0
    ("make check || exit 256", True),  # 0, as the status is N modulo 256
    ("make check || { echo red || exit 1; }", True),  # 0
    ("make check || false; echo after", True),  # 0
    ("make check || false || true", True),  # 0
    ("make check || exit 1 | tail -1", True),  # 0: a pipeline stage is a subshell
    ("( make check || exit 1 ); echo after", True),  # 0: the `exit` leaves the subshell
    ("for t in a b; do make check || exit 1; done | tail -1", True),  # 0: so is a piped loop
)


@pytest.mark.parametrize(("command", "refused"), FALLBACKS)
def test_a_fallback_that_fails_too_keeps_the_status(command: str, refused: bool) -> None:
    """An `||` fallback that exits non-zero hands the failure on, read as bash runs it (`PL-KQ4Q`).

    Every fallback was read as one that succeeds, so `make check || exit 1`,
    the ordinary way to stop on a red gate, was refused for losing what it
    keeps. A fallback passes only where it provably fails, and an `exit` ends
    only the shell running it, which is not the whole string inside a subshell
    or a piped loop.
    """
    decision = _decision(command)
    assert (decision is not None) is refused, f"{command!r}: refused={decision is not None}"


PIPESTATUS_READ = (
    # `PL-1DW7`'s command, verbatim: `PIPESTATUS` holds the status of every
    # stage of the pipeline run last, so the `echo` prints `make`'s own
    # whatever `tail` did, and it was refused at the `|`. The comment is what
    # bash 5.2.21 printed with the gate a stub exiting 3.
    ('make docket 2>&1 | tail -4; echo "exit=${PIPESTATUS[0]}"', False),  # exit=3
    # The first stage's element by its other names, every element, a copy, a
    # newline for the `;`, and a gate with no pipe after it.
    ('make check 2>&1 | tail -45; echo "exit=${PIPESTATUS[@]}"', False),  # exit=3 0
    ('make check 2>&1 | tail -45; echo "exit=${PIPESTATUS[*]}"', False),  # exit=3 0
    ('make check 2>&1 | tail -45; echo "exit=$PIPESTATUS"', False),  # exit=3
    ('make check 2>&1 | tail -45; codes=("${PIPESTATUS[@]}")', False),  # codes holds 3 0
    ('make check 2>&1 | tail -45\necho "exit=${PIPESTATUS[0]}"', False),  # exit=3
    ('make check > /tmp/gate.log 2>&1; echo "exit=${PIPESTATUS[0]}"', False),  # exit=3
    # Under `pipefail` too, which carries the walk to the pipeline's end first.
    ('set -o pipefail; make docket 2>&1 | tail -4; echo "exit=${PIPESTATUS[0]}"', False),  # exit=3
    # On every pass of a loop, and past a stage that is a group.
    (
        'for t in a b; do uv run pytest -q $t 2>&1 | tail -5; echo "exit=${PIPESTATUS[0]}"; done',
        False,  # exit=3, twice
    ),
    ('make check 2>&1 | { tail -45; }; echo "exit=${PIPESTATUS[0]}"', False),  # exit=3
    # Another stage's status, or none read straight after the pipeline.
    ('make check 2>&1 | tail -45; echo "exit=${PIPESTATUS[1]}"', True),  # exit=0, tail's
    ('echo t.py | uv run pytest -q 2>&1 | tail; echo "exit=${PIPESTATUS[0]}"', True),  # exit=0
    ('make check 2>&1 | tail -45; git status; echo "exit=${PIPESTATUS[0]}"', True),  # git's
    ('make check 2>&1 | tail -45 & echo "exit=${PIPESTATUS[0]}"', True),  # exit=, none ran yet
    ('(make check 2>&1 | tail -45); echo "exit=${PIPESTATUS[0]}"', True),  # exit=0, the subshell's
    # A read that runs only on the last stage's answer, or not at all: the
    # `&&` and the `then` printed exit=3, and print nothing where `tail`
    # fails; the rest printed nothing. Each string exits 0.
    ('make check 2>&1 | tail -45 && echo "exit=${PIPESTATUS[0]}"', True),
    ('make check 2>&1 | tail -45 || echo "exit=${PIPESTATUS[0]}"', True),
    ('if make check | tail; then echo "exit=${PIPESTATUS[0]}"; fi', True),
    ('until make check | tail; do echo "exit=${PIPESTATUS[0]}"; done', True),
    ('if true; then make check | tail; else echo "exit=${PIPESTATUS[0]}"; fi', True),
    ('if true; then make check | tail; elif [ "${PIPESTATUS[0]}" = 0 ]; then :; fi', True),
)


@pytest.mark.parametrize(("command", "refused"), PIPESTATUS_READ)
def test_pipestatus_read_after_the_pipeline_keeps_the_status(command: str, refused: bool) -> None:
    """A gate's status read out of `PIPESTATUS` after its pipeline survives the pipe (`PL-1DW7`).

    The walk knew one reader, a `$?` in the segment straight after a
    separator, so the met command was refused at the `|` although its `echo`
    prints `make`'s own status. Only the first stage's status is read, and only
    by the command after the `;` that ends the pipeline, which runs whatever
    the pipeline returned.
    """
    decision = _decision(command)
    assert (decision is not None) is refused, f"{command!r}: refused={decision is not None}"


AND_THEN_A_PIPE = (
    # `PL-0FGH`'s command, its elisions filled in: `|` binds tighter than `&&`,
    # so the `grep` is the last stage of the push, and a failing `make` skips
    # the push and the `grep` both. Each comment is the exit bash 5.2.21 gave
    # with the gate a stub exiting 3, and the second field is what the refusal
    # says of the separator that loses the status, where one does.
    (
        "make doc-check > /tmp/doc.log 2>&1 && git add docs/items && git commit -qm x "
        "&& git push -q origin HEAD 2>&1 | grep -v remote",
        None,
    ),  # 3
    # The `&&` the refusal recommends, with a pipe on the step after it.
    ("make check > /tmp/gate.log 2>&1 && tail -45 /tmp/gate.log | grep -i error", None),  # 3
    ("make check && git status | head -3", None),  # 3
    # A stage that is a group, a gate ending a pipeline of its own, a second
    # piped step, and a fallback that fails too ahead of the `&&`.
    ("make check && { git status; } | head -3", None),  # 3
    ("make check && ( git status ) | head -3", None),  # 3
    ("true | make check && git status | head -3", None),  # 3
    ("make check && git status | head -3 && git log --oneline | head -1", None),  # 3
    ("make check || false && git status | head -3", None),  # 1
    # What follows the skipped pipeline decides, as it would straight after
    # the gate.
    ('make check && git status | head -3; echo "exit=$?"', None),  # prints exit=3
    ("make check && git status | head -3; echo after", "after the `;`"),  # 0
    ("make check && git status | head -3 || true", "fallback succeeds"),  # 0
    ("make check && git status | head -3 &", "backgrounded"),  # 0
    # And a `|` after a group the gate is inside pipes the group.
    ("( make check && git status ) | head -3", "LAST stage"),  # 0
    ("{ make check && git status; } | head -3", "LAST stage"),  # 0
    ("( make check && git status | head -3 ) | cat", "LAST stage"),  # 0
)


@pytest.mark.parametrize(("command", "loses"), AND_THEN_A_PIPE)
def test_a_gate_before_and_skips_the_whole_pipeline_after_it(
    command: str, loses: str | None
) -> None:
    """`|` binds tighter than `&&`, so a failing gate skips the whole pipeline after it (`PL-0FGH`).

    The walk stepped over one command after the `&&` and read the `|` behind
    it as losing the status of the gate, so every command here that bash
    exits non-zero on was refused, and the rest were refused at that `|`
    rather than at the separator that loses the status.
    """
    decision = _decision(command)
    if loses is None:
        assert decision is None, f"{command!r} was refused"
    else:
        assert decision is not None, f"{command!r} was allowed"
        assert loses in decision["permissionDecisionReason"], command


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


GLUED = (
    # `PL-63TT`'s reproductions. A `)` touching the `;` or `|` after it arrived
    # as one token that was no separator, so the gate after it read as an
    # argument of the command before, and was never checked.
    ("(true); make check 2>&1 | tail -45", True),
    ("(make check)|tail", True),
    ("(cd sub && uv run pytest -q); make check 2>&1 | tail -30", True),
    # `|&` is a pipe that carries stderr too, and was no separator at all.
    ("make check |& tail", True),
    # Longest match keeps a redirection whole: `>|`, `&>` and `&>>` end no
    # command, so the `echo` still reads the gate's own status.
    ('make check >| /tmp/gate.log; echo "exit=$?"', False),
    ('make check &> /tmp/gate.log; echo "exit=$?"', False),
    ('make check &>> /tmp/gate.log; echo "exit=$?"', False),
)


@pytest.mark.parametrize(("command", "refused"), GLUED)
def test_a_glued_punctuation_run_splits_into_bash_operators(command: str, refused: bool) -> None:
    """A run of `();<>|&` is split into bash's operators, longest first (`PL-63TT`).

    Split one character at a time instead, `>|` would be a pipe and `&>` a
    background launch, and each of the last three would be refused.
    """
    decision = _decision(command)
    assert (decision is not None) is refused, f"{command!r}: refused={decision is not None}"


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


HEREDOCS = (
    # `PL-39LD`'s shape: an item body written through a python3 heredoc.
    "python3 - <<'EOF'\nprint('Run make check 2>&1 | tail -45')\nEOF\n",
    # `<<-` strips the leading tabs of the body's lines and of the terminator.
    "cat <<-EOF\n\tRun make check 2>&1 | tail -45\n\tEOF\n",
    # A quoted delimiter is the word with its quotes removed.
    'cat <<"EOF"\nRun make check 2>&1 | tail -45\nEOF\n',
    "cat <<\\EOF\nRun make check 2>&1 | tail -45\nEOF\n",
    # Two on one line: both bodies go, in order.
    "cat <<A <<B\nRun make check | tail\nA\nRun make check | tail\nB\n",
    # Inside a double-quoted `$( )`, whose quotes and heredoc are its own: the
    # shape of every commit message this repository writes.
    'git commit -m "$(cat <<\'EOF\'\nPL-D0W8: "make check | tail" loses it\nEOF\n)"\n',
)


@pytest.mark.parametrize("heredoc", HEREDOCS)
def test_only_a_heredoc_body_is_removed(heredoc: str) -> None:
    """The body is document content, and the lines after its terminator are commands again.

    Each hook cut the command at its first `<<`, so a check run after a heredoc
    in the same call was never read: `PL-39LD`'s session ran `make docket 2>&1
    | tail -4` after a python3 heredoc, unrefused, and read `tail`'s exit 0.
    """
    assert _decision(heredoc + "git status") is None, "the body was read as commands"
    after = heredoc + 'make docket 2>&1 | tail -4; echo "exit=$?"'
    assert _decision(after) is not None, "the command after the terminator was not read"


NOT_A_HEREDOC = (
    'cat <<< "a here-string"; make check 2>&1 | tail -45',
    'echo "a << b"; make check 2>&1 | tail -45',
    "echo '<<EOF'; make check 2>&1 | tail -45",
)


@pytest.mark.parametrize("command", NOT_A_HEREDOC)
def test_a_here_string_or_a_quoted_introducer_hides_nothing(command: str) -> None:
    """`<<<` is a here-string and a quoted `<<` is text, so neither opens a body to remove."""
    assert _decision(command) is not None, f"{command!r} was allowed"


def test_an_unterminated_heredoc_runs_to_the_end() -> None:
    """Bash reads a body with no terminator line to the end of the input, so this fails open."""
    assert _decision("cat <<EOF\nmake check 2>&1 | tail -45") is None


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
    assert "`exit 1` or `false`" in _decision("make check || true")["permissionDecisionReason"]


def test_the_refusal_names_the_gate_it_caught() -> None:
    """One message serves every guarded command, so it has to say which one fired."""
    assert "`uv run pytest`" not in _decision("uv run pytest | tail")["permissionDecisionReason"]
    assert "runs `pytest`" in _decision("uv run pytest | tail")["permissionDecisionReason"]
    assert "runs `mypy`" in _decision("uv run mypy | tail")["permissionDecisionReason"]
    assert (
        "runs `bin/docket check`"
        in _decision("bin/docket check | tail")["permissionDecisionReason"]
    )


REMEDIES = (
    # This item's command, verbatim. Spelled from the gate's name, it was offered
    # `tools/possessive_section_check.py` alone, which exits 126, since no
    # `tools/` script is executable (`PL-ZS13`).
    (
        "python3 tools/possessive_section_check.py --help 2>&1 | tail -4",
        "python3 tools/possessive_section_check.py --help",
    ),
    # The rest of what it reproduced: the runner and the file, a check's
    # subcommand, an id, and an assignment the command set.
    ("uv run pytest -q tests/unit/t.py | tail", "uv run pytest -q tests/unit/t.py"),
    ("python3 tools/doc_check.py check | head -40", "python3 tools/doc_check.py check"),
    ("bin/docket verify PL-D0W8 | tail", "bin/docket verify PL-D0W8"),
    (
        "QT_QPA_PLATFORM=offscreen uv run pytest -q tests/integration 2>&1 | tail -5",
        "QT_QPA_PLATFORM=offscreen uv run pytest -q tests/integration",
    ),
    # A wrapper is how the gate ran. The grouping or reserved word opening it,
    # the `)` of a subshell around it and its redirections are not.
    ("timeout 600 make check | tail -5", "timeout 600 make check"),
    ("cd /r && (make check) 2>&1 | tail", "make check"),
    ("if make check 2>&1 | tail -45; then echo green; fi", "make check"),
    ("2>/dev/null uv 2>&1 run mypy | tail", "uv run mypy"),
    # A word quoted to hold a blank is quoted again - an assignment's value
    # alone, and one holding a `$` in double quotes, so it expands as it did -
    # and a bare one stays bare.
    (
        'uv run pytest -q t.py -k "a and not b" 2>&1 | tail -12',
        "uv run pytest -q t.py -k 'a and not b'",
    ),
    ('FOO="a b" make check | tail', "FOO='a b' make check"),
    ('uv run pytest -q "$(cat /tmp/files)" | tail', 'uv run pytest -q "$(cat /tmp/files)"'),
    ("for t in a b; do uv run pytest -q $t; done", "uv run pytest -q $t"),
    # And the command `PL-2JRC` ran comes back as it was.
    ("make check 2>&1 | tail -45", "make check"),
)


@pytest.mark.parametrize(("command", "spelled"), REMEDIES)
def test_the_remedy_runs_the_gate_the_command_ran(command: str, spelled: str) -> None:
    """Each remedy spells the gate as the refused command ran it, and is admitted (`PL-ZS13`).

    The lines were spelled from the gate's name, so a check run through
    `python3` came back as a script that is not executable, which exits 126,
    and `uv run pytest` on one file as bare `pytest` over the whole suite. The
    header promises every remedy is admitted, so each is piped back in.
    """
    reason = _decision(command)["permissionDecisionReason"]
    assert f"\n    set -o pipefail; {spelled} 2>&1 | tail -45\n" in reason
    assert f"\n    {spelled} > /tmp/gate.log 2>&1 " in reason
    assert f"(`{spelled} && tail -45 /tmp/gate.log`)" in reason
    remedies = [line.strip() for line in reason.splitlines() if line.startswith("    ")]
    assert len(remedies) == 2, reason
    for remedy in remedies:
        assert _decision(remedy) is None, f"{command!r} was offered {remedy!r}, which is refused"


def test_a_gate_run_with_an_unquoted_substitution_is_named_and_says_so() -> None:
    """The one gate `shell_split.command_line` does not spell back: the quoting inside is gone.

    Named alone, the lines do not run what the command ran, so the refusal says
    so rather than letting them pass for a copy of it.
    """
    reason = _decision("uv run pytest -q $(cat /tmp/files) | tail")["permissionDecisionReason"]
    assert "\n    set -o pipefail; pytest 2>&1 | tail -45\n" in reason
    assert "does not spell back" in reason
    spelled = _decision("uv run pytest -q t.py | tail")["permissionDecisionReason"]
    assert "does not spell back" not in spelled


# Why each spelling below is outside the promise the hook's header opens with,
# naming what found it.
NEGATED = (
    "a `!` ahead of a gate turns its answer over, is written nowhere here, and no session "
    "is known to have written one: `PL-W9XN`, found working `PL-KQ4Q`"
)
UV_OPTIONS = (
    "`uv run` with options of its own is written nowhere here and met by no session: "
    "`PL-QMN0`, found triaging `PL-TRMN`. Its fix, which carries uv 0.12.19's option "
    "grammar, is `59ea9d1c`, the head of `#1127` on `claude/project-thread-qt3onr`, ready "
    "to rebase if the spelling is met"
)
NOT_RESERVED = (
    "`time` or `!` after an assignment or a redirection, ahead of a `set`, is written "
    "nowhere here and met by no session: `PL-DCHW`, found closing `PL-9RSP`"
)
AS_A_MODULE = (
    "a listed gate run as `python -m` is written nowhere here and met by no session: "
    "`PL-7PB9`, found working `PL-QMN0` on `claude/project-thread-qt3onr`"
)
DOCKET_OPTIONS = (
    "`bin/docket` with its own options ahead of the subcommand is a line argparse admits "
    "and nobody writes: `PL-BM3Z`, found working `PL-QMN0` on `claude/project-thread-qt3onr`"
)
UNMATCHED = (
    "a gate built out of a variable, or run by a wrapper `shell_split.WRAPPERS` does not "
    "name, is written nowhere here, and was left unmatched on purpose by `PL-TRMN`"
)
IN_A_STAGE = (
    "a `$?` read in a later stage of the gate's own pipeline is written nowhere here and met "
    "by no session: found working `PL-1DW7`"
)
QUOTED_READ = (
    "a status read written inside single quotes, which print it as text, is written nowhere "
    "here and met by no session, and the guard reads each word with its quotes removed: found "
    "working `PL-1DW7`"
)
LOSES = "exits 0 when the gate fails, with the status of the `tail` it is piped to"

# Spellings outside the promise, each read wrongly today (`PL-61FT`): the
# command, whether it is refused today, what bash does with it, and why it is
# outside. A session probing the guard records what it finds here rather than
# filing it, and a row becomes an item only once a session is seen writing it.
# Each exit is bash 5.2.21's with the gate a stub exiting 3.
KNOWN_GAPS = (
    ("! make check", False, "exits 0 when the gate fails, since `!` inverts it", NEGATED),
    ("! make check && echo ok", False, "exits 0 when the gate fails, and runs the `echo`", NEGATED),
    ("! make check || exit 1", False, "exits 0 when the gate fails, and skips the `exit`", NEGATED),
    ("uv run --with pytest-xdist pytest -n 4 2>&1 | tail", False, LOSES, UV_OPTIONS),
    ("uv run --frozen mypy | tail", False, LOSES, UV_OPTIONS),
    ("uv run -m pytest | tail", False, LOSES, UV_OPTIONS),
    ("uv -q run pytest -q 2>&1 | tail", False, LOSES, UV_OPTIONS),
    (
        "FOO=1 time set -o pipefail; make check 2>&1 | tail -5",
        False,
        "exits 0 when the gate fails: after an assignment `time` names a program, which is "
        "not found, so no `set` runs",
        NOT_RESERVED,
    ),
    (
        "2>/dev/null time set -o pipefail; make check 2>&1 | tail -5",
        False,
        "exits 0 when the gate fails: after a redirection `time` names a program, which is "
        "not found, so no `set` runs",
        NOT_RESERVED,
    ),
    (
        "FOO=1 ! set -o pipefail; make check 2>&1 | tail -5",
        False,
        "exits 0 when the gate fails: after an assignment `!` names a command, which is not "
        "found, so no `set` runs",
        NOT_RESERVED,
    ),
    ("python3 -m pytest -q 2>&1 | tail", False, LOSES, AS_A_MODULE),
    ("python3 -m mypy | tail", False, LOSES, AS_A_MODULE),
    ("python -m ruff check . | tail", False, LOSES, AS_A_MODULE),
    ("uv run python -m mypy | tail", False, LOSES, AS_A_MODULE),
    ("bin/docket --no-fetch check 2>&1 | tail -3", False, LOSES, DOCKET_OPTIONS),
    ("bin/docket --no-fetch verify PL-QMN0 | tail", False, LOSES, DOCKET_OPTIONS),
    ("bin/docket --items docs/items check | tail", False, LOSES, DOCKET_OPTIONS),
    ('gate="make check"; $gate | tail', False, LOSES, UNMATCHED),
    ("stdbuf -oL make check | tail", False, LOSES, UNMATCHED),
    (
        'make check | echo "exit=$?"',
        False,
        "exits 0 when the gate fails, and prints exit=0: in a pipeline stage `$?` is the status "
        "of the command before the pipeline",
        IN_A_STAGE,
    ),
    (
        "make check; echo 'exit=$?'",
        False,
        "exits 0 when the gate fails, and prints the text exit=$?",
        QUOTED_READ,
    ),
    (
        "make check 2>&1 | tail -45; echo 'exit=${PIPESTATUS[0]}'",
        False,
        "exits 0 when the gate fails, and prints the text exit=${PIPESTATUS[0]}",
        QUOTED_READ,
    ),
)


@pytest.mark.parametrize(("command", "refused", "effect", "outside"), KNOWN_GAPS)
def test_a_known_gap_keeps_todays_verdict(
    command: str, refused: bool, effect: str, outside: str
) -> None:
    """A spelling outside the promise gets the verdict it was recorded with (`PL-61FT`).

    What is pinned is the record, not the behaviour - and not as `xfail`, which
    `bin/docket verify --self` counts as a suppressed test. A change that closes
    a gap, meant or not, fails here: the row then moves into the tables above,
    and the promise in the hook's header is widened to hold it.
    """
    assert "PL-" in outside, f"{command!r}: name the item or branch that found it"
    decision = _decision(command)
    assert (decision is not None) is refused, (
        f"{command!r} is a known gap recorded as {'refused' if refused else 'admitted'} "
        f"({outside}), and it no longer is. Run, it {effect}. Move the row into the tables "
        "above, and widen the promise in the hook's header to hold it."
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
