---
id: PL-62PF
title: tools/import_boundary_check.py fails with a SyntaxError (multiple exception types must be parenthesized) under the container's python3 3.13.18 and passes under uv run python, so a session that runs it bare reads a crash as a red check
priority: P3
effort: S
status: done
classes: defect
touches: tools/import_boundary_check.py, tests/unit/test_import_boundary_check.py, tools/check_support.py, tools/fixture_id_check.py, tools/literal_home_check.py, tools/regex_check.py, tools/core_vocabulary_check.py
deferred-from: v0.7.0 - the gate runs the check with the project's Python and is unaffected; only a bare run crashes
added: 2026-11-11
closed: 2026-11-14
pr: 2153
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

**Done, 2026-11-14.** Run under the container's bare `python3` 3.13.18 on
2026-11-14, five tools that parse `src/` failed on 3.14 syntax:
`import_boundary_check.py` and `fixture_id_check.py` crashed with a
traceback, and `literal_home_check.py` and `regex_check.py` reported the
`SyntaxError` as a finding. `core_vocabulary_check.py` passed only because the
modules it reads hold no 3.14 syntax yet. `diff_mutation.py` already declines
with "no answer", so it was left alone. The other tools that use `ast` passed.

All five now return 2 with one line that names the Python release the project
needs and the command to use. The release is read from `requires-python` in
`pyproject.toml`, which states it, through one helper,
`tools/check_support.py`'s `source_python_refusal`. The four checks built on
`run_report` ask for it with `parses_source=True`, and `fixture_id_check.py`
calls it directly. So the sibling tools needed no item of their own, and no
generator is recorded: the one fact now has one reader.

The regression test `test_an_older_interpreter_is_named` failed against the
tools before the fix (`git stash -- tools/`, then `uv run pytest -q
tests/unit/test_import_boundary_check.py -k older`) with `assert 0 == 2`.
