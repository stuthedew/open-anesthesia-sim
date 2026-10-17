---
id: PL-ZWQS
title: Re-time quality.yml's split jobs from five slow-runner runs after PL-T9X9 merges: their timeout-minutes, main_ci_status's pytest baseline, and whether the two parts finish within about 20 s of each other
priority: P3
effort: S
status: ready
feature: ci-cost
touches: .github/workflows/quality.yml, tools/main_ci_status.py
added: 2026-10-17
payoff: quality.yml's timeouts and the pytest drift line's baseline match what the split jobs actually take
not-delegable: the end state is a measurement of CI runs on GitHub, which no local command can take
---

**Problem.** `PL-T9X9` split `quality.yml`'s pytest step into two jobs,
`checks-part-1` and `checks-part-2`, and made `checks` the job that combines
their coverage. Three things in the tree were sized before the split ran on
`main`, and can be re-timed only from its runs:

- Both parts keep the single job's `timeout-minutes: 15`, which was sized
  against that job's longest run of 639 s. Each part now runs about half of
  the work. `checks` has 5 minutes, sized on an estimate of about 30 s.
- `tools/main_ci_status.py`'s `PYTEST_BASELINE_S = 470` is the single step's
  median. The drift line now sums the two parts' pytest steps. The sum should
  sit a little above 470 s, because each part pays its own collection and
  worker start-up. That is inside the line's band, but it is not measured.
- `tests/conftest.py` gives all 46 tests that read a costly computation to
  part 2. On a slow runner the two parts were estimated to finish within about
  20 s of each other.

**Why it matters.** A timeout that is too loose lets a hung step hold a runner
for 15 minutes. A baseline a few percent off narrows the band the drift line
reads. Parts that finish far apart lose part of the saving.

**Done when.** Over at least five successful slow-runner runs on `main` after
the split, the median time from the first job's start to the end of `checks`
is recorded here against the single job's 621 s median, with the reason if
the saving is less than 3 minutes. Each `timeout-minutes` is restated from the
longest of those runs, with headroom like the old one's 41%. The parts'
pytest steps are compared, and `PYTEST_BASELINE_S` is re-measured the way its
comment says once 100 runs exist, or kept with the reading that shows it still
fits.

**Generator check.** Follow-up work to a change the owner asked for, not a defect: no reader misread a fact. The numbers were sized before the runs that measure them existed.
