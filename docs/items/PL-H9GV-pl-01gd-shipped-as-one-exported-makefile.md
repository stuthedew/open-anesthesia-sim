---
id: PL-H9GV
title: PL-01GD shipped as one exported Makefile variable with no test: PYTHONDONTWRITEBYTECODE appears only at Makefile:21, its declared touches names tests/unit/test_tools_portability.py which never changed, and its verify: passes against an untouched suite
priority: P2
effort: S
status: done
classes: defect, test
feature: dev-tooling
touches: tests/unit/test_bytecode_guard.py, Makefile
added: 2026-09-12
closed: 2026-09-27
pr: 1178
verify: grep -q 'def test_the_makefile_turns_bytecode_writing_off_for_its_recipes' tests/unit/test_bytecode_guard.py
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

**Done when.** `tests/unit/test_bytecode_guard.py` asserts that the Makefile
exports `PYTHONDONTWRITEBYTECODE` to its recipes, so removing the line turns a
test red rather than returning a `make check` failure nobody can trace to its
source. (It named `tests/unit/test_tools_portability.py` until the
re-confirmation below.)

**Re-pointed by `PL-6TP8`, 2026-09-19.** The contract is why `PL-01GD`'s
command is not re-pointed: a closed item's `verify:` is the record of what
ran, and a command that passed against an untouched suite is the
non-discriminating shape the contract's first obligation names, recorded here
as an instance. The test this item owes is ordinary work and stands as briefed.

**Re-confirmed, 2026-09-27 - changed shape.** The export still stands
untested, as the `Makefile`'s `export PYTHONDONTWRITEBYTECODE := 1`, but it no
longer carries the guard alone. `PL-0MLZ` (#1168) moved the pytest half into
the root `conftest.py`, which turns bytecode off for every pytest run however
it is started, and made `tests/unit/test_bytecode_guard.py` to hold it. What
the export still guards is the recipes that are not pytest runs - `bin/docket
check` under `make docket` imports the `docket` package from source - and
`PL-0MLZ`'s brief ends by saying this item owes it the test. Two things change:

- **The test lives in `tests/unit/test_bytecode_guard.py`**, which exists for
  this guard and did not when this brief was filed.
  `tests/unit/test_tools_portability.py` holds the tools' promise to parse and
  run at the floor interpreter, a different one, and was named here only
  because `PL-01GD` had declared it.
- **The `verify:` greps for the test by name.** The variable's name already
  appears in `test_bytecode_guard.py`, so a grep for it would pass before the
  work, which is `PL-01GD`'s non-discriminating shape again.

**Approach.** The test asks `make` what a recipe sees rather than reading the
`Makefile`'s text: a probe recipe read after it from a second `-f` prints the
variable from its own shell. A dropped `export`, an `unexport`, or the line
moving under a false conditional fails it, and respelling the line does not.
This run exports the variable itself, so the probe's environment drops it and
every `MAKE*` variable, and the same probe without the `Makefile` is the
control showing it did. Without `make` on PATH it fails saying so, since a skip
is a suppression `docket verify` refuses and `make check` could not run there
either. The `Makefile`'s comment names the test, so a tidy meets the reason
before the red.

**Built, 2026-09-27.** Three edits to the `Makefile` were each run against the
new test and each turned it red alone: deleting the line, dropping its
`export`, and adding an `unexport` after it. It passes under an enclosing
`make`, where the variable arrives from two places, and the control fails if
the probe's environment is not cleared. A `make` that cannot read the probe
fails with its own error message rather than a bare exit status.
