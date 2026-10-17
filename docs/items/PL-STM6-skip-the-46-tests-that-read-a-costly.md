---
id: PL-STM6
title: Skip the 46 tests that read a costly computation on pull requests that touch no simulator path, and rebalance quality.yml's two parts when they are skipped
priority: P3
effort: M
status: ready
feature: ci-cost
touches: .github/workflows/quality.yml, tests/conftest.py
added: 2026-10-17
payoff: a pull request that touches no simulator code waits about a minute less for checks
not-delegable: the design names the paths that count as simulator code, a judgment, and its end state is a measurement of CI runs
---

**Tabled** (project owner, 2026-10-17: "I want low hanging fruit. Not a new
headache to trouble shoot for two minutes savings"). It saves about a minute per run and needs a design round on which paths count as simulator code. Pick it up only if
CI time becomes a problem again.

**Problem.** 46 tests read a costly computation: the readers of the 8
washout curves in `tests/reference/test_late_washout_against_published_fits.py`
and of the two controller runs in `tests/integration/test_controller.py`. In a
4-core container on 2026-10-17 they took about 22% of the suite's time, 294 s
with them and 229 s without, one run each. `core/` stayed at 100% of
statements and branches without them. Of the 113 merges to `main` from
2026-10-10 to 2026-10-17, 89 touched none of `src/`, `app/`,
`tests/reference/` or `tests/integration/`, so those 46 tests could not have
changed result on them.

**Why it matters.** Since `PL-T9X9`, all 46 run in `checks-part-2`. Skipping
them there alone saves little, because `checks-part-1` then becomes the
longer job. If the parts are also rebalanced when the tests are skipped, the
saving is about half of the 110 s they cost a slow runner, so about 55 s per
run on about 79% of pull requests. That is an estimate, not a measurement.
Running only the tests a change can affect is the test-selection practice in
Memon et al., "Taming Google-Scale Continuous Testing", ICSE-SEIP 2017,
https://doi.org/10.1109/ICSE-SEIP.2017.16.

**Design to settle.** Which paths count as touching the simulator: at least
the four directories above, `pyproject.toml` and `uv.lock`, since a
dependency change can change a result. A path the rule does not recognise must
run everything. A push to `main` always runs everything. If a later change
leaves a line of `core/` covered only by one of these tests, the combined
coverage gate fails on every pull request that skips them, so the rule needs
an answer for that before it is built.

**Done when.** On a pull request whose diff touches no listed path, CI skips
the 46 tests and rebalances the parts, pushes to `main` still run them, and the
median slow-runner time of such pull requests is measured against the split's.

**Generator check.** An optimisation the owner agreed to file, not a defect: no reader misread a fact.
