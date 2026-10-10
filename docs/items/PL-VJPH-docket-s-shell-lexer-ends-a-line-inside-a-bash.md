---
id: PL-VJPH
title: docket's shell lexer ends a line inside a bash process substitution or a compound array assignment carried across lines, so script_lines hands doc_check the substitution's tail and each array element as commands where bash 5.2 runs one command; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: .claude/hooks/shell_split.py, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/gate-status-guard.sh, .claude/hooks/no-prune-guard.sh, .claude/hooks/push-check-guard.sh, subprojects/docket/src/docket/shell.py, subprojects/docket/src/docket/__init__.py, subprojects/docket/tests/test_shell.py, tests/unit/test_shell_reader.py, tests/unit/test_doc_check.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_no_prune_guard.py, tests/unit/test_push_check_guard.py, docs/ARCHITECTURE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
closed: 2026-10-10
pr: 1390
payoff: a process substitution or an array assignment carried across lines reads as the one command bash runs, so doc_check never takes its tail or an element for a script CI runs
verify: grep -qF '"shell lines, a process substitution carried across lines"' tests/unit/test_doc_check.py && grep -qF '"shell lines, an output process substitution carried across lines"' tests/unit/test_doc_check.py && grep -qF '"shell lines, an array assignment carried across lines"' tests/unit/test_doc_check.py
---

**Problem.** docket's shell lexer ends a line inside a bash process substitution or a compound array assignment carried across lines, so script_lines hands doc_check the substitution's tail and each array element as commands where bash 5.2 runs one command; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`docket.shell`, the shared shell reader. `_Lexer.read` records a line break at a
newline unless a substitution has raised its nesting, which only `$(` and a
backquote do. A process substitution, `<(` or `>(` (Bash Reference Manual
§ 3.5.6), and a compound array assignment, `name=(` (§ 6.7), are read as plain
operators with no nesting, though each holds newlines and its command goes on
after the closing parenthesis. The module names bash as its reference; dash
refuses both forms.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against bash 5.2.21:

```text
echo <(echo a
) tools/doc_check.py

files=(
  tools/doc_check.py
  tools/dead_ends.py
)
echo "${files[@]}"
```

`script_lines` cut the first script into `echo <(echo a` and `)
tools/doc_check.py`, and `doc_check._shell_commands` read the second piece as a
command running `tools/doc_check.py`; it cut the second into `files=(`, each
element and `)`, so each array element read as a command. `bash -x` shows one
command each, `echo /dev/fd/63 tools/doc_check.py` and `files=(tools/doc_check.py
tools/dead_ends.py)`. Latent: no tracked file leaves `<(`, `>(` or `name=(` open
at a line end.

**Reproduced 2026-10-10 at triage** on this branch at `b6b9c382`, whose readers are `main`'s at `fe2e5132`: `script_lines` cut
`echo <(echo a` from `) tools/doc_check.py`, `tee >(cat` from `) < /dev/null
tools/doc_check.py`, and the array into `files=(`, each element and `)`.

**Why it matters.** `script_lines` is how `tools/doc_check.py` reads what a
workflow's `run:` steps and a Markdown fence execute, and `check_gate_parity`
takes the scripts each piece runs from its first word on. So a substitution's
tail or an array's element read as a command of its own is a script the merge
gate is taken to run: `tools/doc_check.py` above reads as run by CI where bash
hands it to `echo` as an argument.

**Generator check.** A member of `PL-R417`: the one shell reader ends a
statement at a newline bash carries it past. The hooks' `shell_split` is the
other copy (`PL-JNYL`), whose gaps its own policy records rather than files.

**Done when.** `_Lexer` counts `<(`, `>(` and an assignment's `(` as nesting, as
it counts `$(`, pinned by a `shell lines, ` case in `PL-R417`'s guard for each
form, failing on today's reader.

**Decided 2026-10-06.** Fixed once, in the shell reader `PL-JNYL` merges from
the hooks' and docket's two, which opens `PL-R417`'s shell batch (project
owner, 2026-10-06, ratified, over fixing each shell reader in place).

**Built 2026-10-10 (`#1390`).** Fixed once, in the merged reader: `_Lexer`
counts `<(`, `>(` and an array assignment's `(` as nesting, as it counts `$(`,
so a newline inside one carries the line on, and a comment inside an
assignment's list ends at its newline without ending the list. Three
`shell lines, ` cases in `PL-R417`'s guard pin an input process substitution,
an output one and an array assignment, each carried across lines and each
failing on `main`'s reader, which cut it into pieces.
