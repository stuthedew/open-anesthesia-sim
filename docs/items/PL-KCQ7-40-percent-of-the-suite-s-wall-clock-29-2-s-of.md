---
id: PL-KCQ7
title: 40 percent of the suite's wall clock (29.2 s of 70 s) tests subprojects/docket, so the workflow apparatus dominates the simulator's own gate
priority: P3
effort: S
status: done
classes: perf
touches: subprojects/docket/tests
feature: dev-tooling
added: 2026-09-03
closed: 2026-09-04
not-delegable: the outcome is a decision to change nothing, so there is no state a command could find different afterwards. The only command available would grep this file for its own conclusion, which proves the sentence was written rather than that the ratio is acceptable - and whether it is acceptable is the judgment the item exists to record
---

**Problem.** Measured 2026-09-03 on four cores, before `PL-WCZV` put `-n auto`
on the suite: `tests/` (the simulator) took 40.8 s and
`subprojects/docket/tests` took 29.2 s of a 70 s run. So two fifths of the
project's most expensive check tests the workflow apparatus rather than the
thing the project is for.

**Why it matters, and why it is P3 rather than higher.** `CLAUDE.md` holds the
simulator and the apparatus to deliberately unequal standards - the apparatus
to "working reliably and staying streamlined" - and this is the clearest
measure yet of what the apparatus costs the simulator. But it is a ratio, not a
defect: those tests are the reason `docket` is trustworthy enough to be relied
on, and `PL-LXR3`, `PL-T940` and `PL-VG7G` are each a case where the suite
caught a check that would have lied.

`PL-WCZV` also changed the arithmetic that made this look urgent. The whole
suite now runs in 26.9 s rather than 70 s, so docket's share is roughly the
same fraction of a much smaller number, and the largest item in `make check` is
now `bin/docket check` instead (`PL-8BFV`). This is worth knowing and is not
worth acting on by itself.

**Where.** `subprojects/docket/tests` - `test_cli.py`, `test_vcs.py` and
`test_verify.py` are the three largest files and `test_verify.py` is the one
that shells out most.

**Options, none recommended yet.** Leave it, which is a real answer and
probably the right one. Or narrow the shell-outs in `test_verify.py`, which are
what make it slow and are also what make it honest. Or split the apparatus
suite out of the default `testpaths` so `make test` runs the simulator alone -
cheap, and it costs the property that one command proves the whole tree.

**Done when.** A decision is recorded, including the decision to accept it as
the cost of a trustworthy queue.

**Decision needed.** Whether to act on the ratio at all. Leaving it is
recommended - `PL-WCZV` took the suite to 26.9 s, so the absolute cost is now
small, and the three named options each trade away something the apparatus is
trusted for. Recording that answer is what closes this; it is here so the ratio
is not rediscovered and treated as new.

**Decided (project owner, 2026-09-04): leave it.** No change to the suite, and
this item exists so the ratio is not rediscovered and treated as new.

The reasoning, recorded because the number will look alarming again to a
session meeting it cold:

- **The absolute cost is now small.** `PL-WCZV` took the whole suite from 70 s
  to 26.9 s locally. docket's share of it is roughly unchanged as a fraction
  and much smaller as a number, and the fraction was never the thing that
  mattered.
- **It is no longer the largest item in either gate.** `bin/docket check` is,
  at 30.5 s of a 59.2 s `make check` and 70 s of a 142 s CI job (`PL-8BFV`).
  A session looking for time to save should look there.
- **The tests are what make the queue trustworthy.** `PL-LXR3`, `PL-T940` and
  `PL-VG7G` are each a case where this suite caught a check that would
  otherwise have reported a clean result while proving nothing - which is the
  specific failure the whole apparatus exists to refuse. The shell-outs in
  `test_verify.py` are the slowest part and are also the part that exercises
  the real subprocess behaviour rather than a mock of it.
- **The three options each cost something real.** Narrowing the shell-outs
  trades the honesty above for seconds. Splitting the apparatus suite out of
  `testpaths` costs the property that one command proves the whole tree, which
  is worth more than the time it saves.

**Revisit if** the apparatus suite grows enough to make `make test` slow again
on its own, or if `subprojects/docket/` stops being actively developed - at
which point its tests would be paying for change that is no longer happening.
