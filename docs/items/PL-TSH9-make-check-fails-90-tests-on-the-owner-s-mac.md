---
id: PL-TSH9
title: make check fails 90 tests on the owner's Mac headless worker host whatever the diff: 87 in subprojects/docket/tests/test_shell.py, 2 in tests/unit/test_makefile_reference.py and 1 in tests/unit/test_branch_sweep.py, so no worker run there can report the gate green
priority: P2
effort: S
status: done
classes: defect
touches: tests/unit/test_branch_sweep.py, tests/unit/test_makefile_reference.py, docs/maintainer.md
deferred-from: v0.6.0 - a workflow-lane test defect outside the layout release
added: 2026-10-19
closed: 2026-10-19
payoff: make check on the owner's Mac passes once bash and GNU make are current, so a worker there sees the failures its own change causes
verify: grep -q 'needs version 4 or newer' tests/unit/test_makefile_reference.py && grep -q 'pack-refs' tests/unit/test_branch_sweep.py && grep -q 'brew install bash make' docs/maintainer.md
---

**Problem.** On the owner's Mac, `make check` failed 90 tests whatever the change. A headless worker found this on 2026-10-19 while working PL-3R6L, and the owner's own run that evening (`~/make-check-mac.log`: 90 failed, 9,764 passed, 3 skipped) gave three causes:

- 87 tests in `subprojects/docket/tests/test_shell.py` compare the lexer with the `bash` on `PATH`, which must be 5.2 or newer. macOS's `/bin/bash` is 3.2.57.
- 2 tests in `tests/unit/test_makefile_reference.py` compare the Makefile readers with GNU make. macOS ships GNU Make 3.81, which quotes a goal as `` `NO_SUCH_GOAL' `` where 4.x writes `'NO_SUCH_GOAL'`. The helper checked only that make was GNU, so the failure named the symptom, not the cause.
- 1 test in `tests/unit/test_branch_sweep.py` pushes `Claude/upper-q7x2kd` beside `claude/done-q7x2kd`. On a filesystem that ignores case, git files the new ref inside the existing loose `claude/` directory and reports it in lower case.

**Why it matters.** A worker on the Mac runs `make check` before it commits. With 90 failures on every run, it cannot see a failure its own change causes, and it spends turns on failures that are not its own. The first worker run missed a real failure in its change this way (#1681).

**Done when.** The two test-side causes are fixed in the tests, and `docs/maintainer.md` names the two tools the Mac needs, how to install them, and how to check them.

**Generator check.** A one-off: three tests that compare against real tools assumed the Linux versions, and no other reader shares a misread fact.
