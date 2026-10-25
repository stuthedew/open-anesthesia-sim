---
id: PL-STM6
title: Skip the 46 tests that read a costly computation on pull requests that touch no simulator path, and rebalance quality.yml's two parts when they are skipped
priority: P3
effort: M
status: ready
feature: ci-cost
touches: .github/workflows/quality.yml, tests/conftest.py, tests/unit/test_worksteal_dealing.py, tests/unit/test_quality_step_order.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, docs/apparatus.md
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

**Taken up again** (project owner, 2026-10-25: "Complete Code quality in the simulator and workflow and CI items", which names this item's feature among the workflow and CI work).

**The design, decided 2026-10-25.** The paths that cannot change these tests' results are `docket.toml`'s `workflow_paths`, the list that already says which files are the apparatus. So no second list is kept for this. `bin/docket ci-scope` gains a third answer, `apparatus`, given when every changed path is under `workflow_paths` and at least one is outside the store. `items` still comes first, because it skips more. A path under neither list, or any reading that cannot show the diff, answers `full` as before. The costly tests read only `src/`, `tests/reference/`, `tests/integration/` and the conftests under `tests/`, and none of those is under `workflow_paths`. Two apparatus files still reach the costly tests: the root `conftest.py`, which runs inside every test, and `quality.yml`, which sets the runner image and the step's environment. A pull request changing only those skips the costly tests, and `main`'s push run, which always runs everything, is the backstop, as it is for the item-only fast path.

`tests/conftest.py` gains `--skip-costly`, which leaves out the tests that `_costly_reads` names. That is the same predicate the parts and the dealing use, so the skipped set cannot drift from the costly set. The second part's pytest step passes it through `PYTEST_ADDOPTS` on `apparatus` only, so the step's name, which `tools/main_ci_status.py` times, does not change.

*The coverage question.* Without the costly tests, `core/` was still covered in full: 1,687 statements and 406 branches, measured locally on 2026-10-25. Coverage still runs on `apparatus`, and `checks` prints it, but it does not hold it to 100% there. Such a pull request changes nothing under `src/` and no simulator test, so it cannot change what covers `core/`. A gap it showed would come from an earlier product change whose line only a costly test reaches, and the apparatus pull request could not fix that without becoming a product one. The blind review of #1773 found that blocking case. Every product pull request and every push to `main` runs the costly tests and holds the full gate. Turning coverage off on `apparatus` was considered and set aside: on Python 3.14 coverage added no measurable time (139 s without it and 128 s with it, on the same 483 tests).

*The balance.* On 2026-10-25 there are 35 costly tests, 28 in the late-washout module and 7 in `test_controller.py`, and they took 479 s of the suite's 1,646 s of summed test time. On arm64 pull requests, part 1's job took a median of 291 s and part 2's 320 s, with part 2's pytest step at 290 s. Part 1 takes 2 of each 5 ordinary tests in 150 s, so part 2's 3 of 5 come to about 225 s and the costly tests to about 65 s of its step. Without them, part 2's job should take about 255 s against part 1's 291 s. That is close enough that `PART_SHARES` is left alone until it is measured.

*Expected saving.* Of the 236 merges to `main` from 2026-10-18 to 2026-10-25, 99 changed apparatus files alone with at least one outside the store, so about 42% of pull requests take this path. Another 64 changed item files alone and already take the item-only fast path. On those the run should finish when part 1 does, about 30 s sooner than now. That is less than the item's first estimate of 55 s, because `PL-928H` moved pull requests to arm64, where part 2 was already only 37 s behind part 1.

**What is left.** Measure the median wall time of apparatus pull requests over at least 20 runs after this merges, against the split's 370 s median on arm64 pull requests (`PL-ZWQS`). Retune `PART_SHARES` for the skip only if part 1 then finishes more than 30 s after part 2.
