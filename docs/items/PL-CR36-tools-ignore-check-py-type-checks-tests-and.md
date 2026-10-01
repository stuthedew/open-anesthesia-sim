---
id: PL-CR36
title: tools/ignore_check.py type-checks tests and subprojects/docket/tests in one mypy invocation, so a second file named conftest in those trees is a duplicate-module error that stops mypy before it evaluates anything and turns make check red
priority: P3
effort: S
status: done
classes: defect
touches: tools/ignore_check.py, tests/unit/test_ignore_check.py
added: 2026-09-21
closed: 2026-10-01
pr: 1259
payoff: a second conftest.py can be added to either test tree without turning make check red for a reason that names the wrong file
verify: grep -q 'def test_a_second_conftest_does_not_stop_mypy' tests/unit/test_ignore_check.py
---

**Problem.** tools/ignore_check.py type-checks tests and subprojects/docket/tests in one mypy invocation, so a second file named conftest in those trees is a duplicate-module error that stops mypy before it evaluates anything and turns make check red

**How it surfaced.** `PL-YRYR` added `subprojects/docket/tests/conftest.py`.
`make check` went red on `Duplicate module named "conftest" (also at
"tests/conftest.py")`, and `ignore_check` reported honestly - `type: ignore
directives: not checked - mypy exited 2 without reporting findings, so nothing
was evaluated` - which is the apparatus floor working, not failing. The tool
declined rather than passing a partial read off as a complete one. What is
wrong is that a legal second `conftest.py` cannot exist in either tree at all.

**The fix, measured 2026-09-21.** `--explicit-package-bases` on `run_mypy`'s
invocation resolves it: with it, mypy derives distinct module names from the
paths and checks 91 source files, reporting the 418 pre-existing type errors
those trees carry - which is exactly what `report()` already filters and the
module docstring already expects ("The several dozen type errors those trees
report, which are why the gate excludes them, pass unread"). Without it, mypy
exits 2 having evaluated nothing.

**Re-measured 2026-10-01: the flag alone now declines.** With
`--explicit-package-bases` and nothing else, mypy reports two
`[import-not-found]` errors, and `report()` reads an unresolved import as "not
checked". `tests/benchmarks/test_frame_cost.py` imports `frame_cost`, and
`tests/reference/test_late_washout_against_published_fits.py` (`PL-KK1Q`,
2026-09-27) imports `test_published_wash_in_and_elimination`, each by bare name
from its own directory, which pytest puts on `sys.path` and the flag takes off
mypy's. Adding those two directories to `MYPY_PATH` resolves both: mypy's
findings over the two trees are then identical to the invocation without the
flag (526 errors in 52 files, 111 source files checked, compared line by line
with line numbers stripped), and the check still reads 32 directives, 0 inert,
with a further `conftest.py` in `subprojects/docket/tests/` and in `tests/unit/`.
A bare sibling import in a third directory declines the same way until its
directory joins `MYPY_PATH`, which the decline's own message names as the
remedy.

**Why it was not fixed inside `PL-YRYR`.** It touches `tools/ignore_check.py`,
outside that item's `touches`, and a tool whose whole job is to decide whether
an answer is sound owes a test for the case that broke it - so both of the
fix-now rule's first two tests fail and it is an item. `PL-YRYR` routed around
it instead by putting its `conftest.py` at the repository root, which is
outside both trees mypy is given; that is a sound place for it on its own
merits and is not a workaround that would need undoing, but it leaves this
latent for whoever adds the next `conftest.py`.

**Done when** a second `conftest.py` may exist in `tests/` or
`subprojects/docket/tests/` without `ignore_check` declining, with a test that
fails on the current invocation.

**Why it matters.** The cost is latent, and the trap is that it presents as an
unrelated failure. `make check` goes red on a duplicate-module error naming two
`conftest.py` paths, and `ignore_check` reports that it evaluated nothing -
honest, and also the loudest line in the output, so a session reads the gate's
decline rather than the one-line cause underneath it. The remedy that presents
itself is to move or rename the new file, which is what `PL-YRYR` did; the
remedy that holds is one flag on the invocation. Until it lands, `tests/` and
`subprojects/docket/tests/` may each hold exactly one `conftest.py` for the life
of the project, which is a constraint nothing states and no check names.
