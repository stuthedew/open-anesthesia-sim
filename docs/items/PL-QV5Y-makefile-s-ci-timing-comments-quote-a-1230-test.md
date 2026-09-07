---
id: PL-QV5Y
title: Makefile's CI-timing comments quote a 1230-test suite at 78 s serial and 27 s parallel, measured 2026-09-03; the suite is now 2096 tests at about 43 s parallel, so a reader sizing a CI-cost decision from them is reading stale figures
priority: P3
effort: S
status: needs-decision
classes: docs
feature: ci-cost
touches: Makefile
added: 2026-09-07
---

**Problem.** Makefile's CI-timing comments quote a 1230-test suite at 78 s serial and 27 s parallel, measured 2026-09-03; the suite is now 2096 tests at about 43 s parallel, so a reader sizing a CI-cost decision from them is reading stale figures

**Why it matters.** Each block is dated and states the suite size it was taken
on, so nothing here misrepresents *when* it was measured. What decays is the
scale a reader carries away. Collected 2026-09-07: 2148 tests, against the 1230
quoted at 2026-09-03 on lines 29-30 and 145-146 and the 1577 quoted at
2026-09-05 on line 35 - 75 percent growth in four days. At that rate any
absolute written into this file is wrong within a week, and nothing fires to
say so.

The arguments the figures support are ratios and all still hold: parallelism is
the largest single item in `check`, `-n auto --dist worksteal` beats either flag
alone, and coverage is identical across both. The exposure is narrower than the
title suggests - a session sizing a *new* CI-cost decision (a runner change, a
suite split, a timeout) from a four-day-old absolute rather than re-measuring,
and taking "78 s serially" as the number to beat.

**Where.** `Makefile`, three blocks and one near-miss:

- lines 29-30, the `check` recipe's parallelism argument (`PL-WCZV`, done);
- lines 35-46, the four-core `-n`/`--dist` table (`PL-VZ8P`, done);
- lines 145-146, the `test` recipe's serial-against-parallel pair (`PL-FX3N`,
  done);
- line 22's 92.8 s against 92.4 s (`PL-22Z3`, done) is a *difference* between
  two runs of the same suite, so it does not date the way an absolute does and
  is probably not in scope.

All four cited items carry the full figures in their own briefs, which is what
makes the second option below cheap: the measurements are already preserved
somewhere that is a historical record by nature.

**Decision needed.** Which of three, and it is a policy choice about the file
rather than an implementation detail:

1. **Re-measure and update.** Keeps the file authoritative and puts it on a
   treadmill nothing maintains; the figures are stale again within a week and
   the next session to notice files this item again.
2. **Keep the argument and the citation, drop the absolutes.** The comments
   keep every claim they make and lose only the part that decays; a reader
   wanting the numbers follows `PL-WCZV`, `PL-VZ8P` or `PL-FX3N` to the item
   that measured them. *Recommended.*
3. **Leave them.** Each is already dated and labelled with its suite size, so a
   reader has what it needs to discount them. Costs nothing and accepts that
   the figures read as current to a reader who skips the date.

**Done when.** The owner has picked one, and the `Makefile` blocks named above
carry no absolute wall-clock or test count that will be wrong within a week
without anything reporting it - either because they no longer carry one, or
because a re-measured one has been written with whatever re-measures it named
beside it.
