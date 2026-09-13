---
id: PL-H9GV
title: PL-01GD shipped as one exported Makefile variable with no test: PYTHONDONTWRITEBYTECODE appears only at Makefile:21, its declared touches names tests/unit/test_tools_portability.py which never changed, and its verify: passes against an untouched suite
priority: P2
effort: S
status: ready
classes: defect, test
feature: dev-tooling
touches: tests/unit/test_tools_portability.py, Makefile
added: 2026-09-12
verify: uv run pytest -q tests/unit/test_tools_portability.py && grep -q 'PYTHONDONTWRITEBYTECODE' tests/unit/test_tools_portability.py
---

**Problem.** PL-01GD shipped as one exported Makefile variable with no test: PYTHONDONTWRITEBYTECODE appears only at Makefile:21, its declared touches names tests/unit/test_tools_portability.py which never changed, and its verify: passes against an untouched suite

**Confirmed at triage, 2026-09-12.** `grep -rn PYTHONDONTWRITEBYTECODE Makefile
tools/ tests/` returns exactly one line, `Makefile:21`, so the variable is
exported and nothing anywhere asserts that it is.

**Why it matters.** `PL-01GD`'s defect was stale `.pyc` bytecode producing a
`make check` failure unreachable from the source in front of the reader - a wrong
answer with complete confidence, which `CLAUDE.md` calls worse than a failure.
The fix is one line in a file nobody reads top to bottom, with no test and no
check, so the next person who tidies the Makefile's exports removes it and the
failure mode returns silently, in exactly the form that is hardest to diagnose.

The second half is worth recording rather than repairing. `PL-01GD` is closed and
its `verify:` is a record of what was run, not a command to re-point - the store
refuses to rewrite a closed item's command for good reason. But that command
passed against a test file the change never touched, so it proved nothing about
the work, and the declared `touches` named a test that never changed. This item
is the honest place to put the test that was owed.

**Done when.** `tests/unit/test_tools_portability.py` asserts that the Makefile
exports `PYTHONDONTWRITEBYTECODE`, so removing the line turns a test red rather
than returning a `make check` failure nobody can trace to its source.
