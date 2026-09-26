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
    # the next command, and an `if`, a loop or a group ends where it closes,
    # not at the first `;` inside it.
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
