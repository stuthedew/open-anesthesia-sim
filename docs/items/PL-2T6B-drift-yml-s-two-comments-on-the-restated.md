---
id: PL-2T6B
title: drift.yml's two comments on the restated-constants job say a run costs four runs of the suite, one for each limit that is not a floor at zero, but #1901 added MAXIMUM_INPUT_FRACTION on 2026-10-31, so run 41279184121 moved five limits and took 31 minutes
priority: P3
effort: S
status: done
classes: docs
milestone: v0.6.13
touches: .github/workflows/drift.yml
added: 2026-11-01
closed: 2026-11-02
pr: 1930
payoff: the recorded reason for running the copied-limit check monthly states what a run really costs
verify: ! grep -qF 'each run costs four runs of' .github/workflows/drift.yml
---

**Problem.** drift.yml's two comments on the restated-constants job say a run costs four runs of the suite, one for each limit that is not a floor at zero, but #1901 added MAXIMUM_INPUT_FRACTION on 2026-10-31, so run 41279184121 moved five limits and took 31 minutes

**Evidence, read 2026-11-01.** `.github/workflows/drift.yml` says "each run
costs four runs of the suite, one for each limit that is not a floor at zero"
above the `restated-constants` job, and "Four runs of the suite, one after
another" above its `timeout-minutes`. `src/anesthesia_sim/core/supported_ranges.py`
now has five limits that are not floors at zero. `MAXIMUM_INPUT_FRACTION`
arrived in `#1901` on 2026-10-31, after `#1778` wrote the comments on
2026-10-25. Run 41279184121 moved all five, from 06:02 to 06:33 UTC.

**Why it matters.** The two comments are the recorded reason for running the
job monthly and the basis of its 240-minute limit. A reader who weighs moving
the job onto pull requests, or checks the limit, reads a cost one run short.
The 240-minute limit still leaves room for five runs.

**Done when.** Both comments give the count from the module rather than a
number that the next limit makes stale, or give five runs and the 31-minute
measurement of 2026-11-01.

**Generator check.** One-off. A comment restated a count that the next limit
changed. That is `PL-4FBP`'s fact at family altitude, in a workflow comment,
which `PL-4FBP`'s convention does not bind.

**Closed 2026-11-02 in #1930.** Both comments in `drift.yml` now say the job
runs the suite once for each limit that is not a floor at zero. They date the
count, five on 2026-11-01, and give the 31 minutes that run 41279184121 took.
