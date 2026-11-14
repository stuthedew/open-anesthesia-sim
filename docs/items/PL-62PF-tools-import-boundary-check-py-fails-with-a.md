---
id: PL-62PF
title: tools/import_boundary_check.py fails with a SyntaxError (multiple exception types must be parenthesized) under the container's python3 3.13.18 and passes under uv run python, so a session that runs it bare reads a crash as a red check
priority: P3
effort: S
status: ready
classes: defect
touches: tools/import_boundary_check.py, tests/unit/test_import_boundary_check.py
deferred-from: v0.7.0 - the gate runs the check with the project's Python and is unaffected; only a bare run crashes
added: 2026-11-11
payoff: a session that runs the import check with the wrong Python is told which one to use, and does not read a crash as a failing check
verify: grep -q 'def test_an_older_interpreter_is_named' tests/unit/test_import_boundary_check.py
---

**Problem.** tools/import_boundary_check.py fails with a SyntaxError (multiple exception types must be parenthesized) under the container's python3 3.13.18 and passes under uv run python, so a session that runs it bare reads a crash as a red check

**Triaged, 2026-11-11.** The tool's own source is not the cause. It parses
the files under `src/`, which use Python 3.14's unparenthesized `except A, B:`
form, and Python 3.13's parser refuses them. `make check` runs the tool with
`uv run python`, which is 3.14, so the gate is unaffected.

**Why it matters.** A session that runs the tool with the container's bare
`python3` sees a traceback and reads it as a failing check, or as a broken
tool.

**Done when.** Run under an interpreter older than the project's
`requires-python`, the tool exits with one line that names the interpreter it
needs and the command to use. Check whether the other tools that parse `src/`
do the same, and file what that finds.

**Generator check.** A one-off so far. The fact is which interpreter can
parse the simulator's source, and no head in `bin/docket generators
--misread` states it. If the sibling tools crash the same way, that is three
readers of one fact, and it is recorded as a generator then.
