---
id: PL-736G
title: On a pull request that changes only apparatus files, CI could skip all 3,891 simulator tests, 1,105 s of the suite's 1,646 s of test time, rather than only the 35 costly ones that PL-STM6 skips: decide whether it should (found working PL-STM6)
priority: P3
effort: S
status: needs-decision
classes: perf, infra
feature: ci-cost
touches: .github/workflows/quality.yml, tests/conftest.py
deferred-from: v0.7.0 - filed after the gate froze; a P3 CI cost waiting on the owner's answer
added: 2026-10-25
payoff: pull requests that change only apparatus files finish about one to two minutes sooner
---

**Problem.** On a pull request that changes only apparatus files, CI could skip all 3,891 simulator tests, 1,105 s of the suite's 1,646 s of test time, rather than only the 35 costly ones that PL-STM6 skips: decide whether it should (found working PL-STM6)

**Evidence.** Measured on 2026-10-25 on one 4-core container at `48c36b64d` with `pytest --junitxml`. A simulator test is one under `tests/reference/` or `tests/integration/`, or one whose module imports `anesthesia_sim`. That is the rule `tools/workflow_paths_check.py` uses for a test file. There were 3,891 simulator tests taking 1,105 s of summed test time, and 6,305 apparatus tests taking 541 s. `PL-STM6` skips the 35 costly tests, 479 s, on a pull request whose every changed path is under `workflow_paths`. Skipping every simulator test there would remove 1,105 s instead, about two thirds of the suite. Of the 236 merges to `main` from 2026-10-18 to 2026-10-25, 99 were such pull requests.

**Why it matters.** On those pull requests, both test parts would shrink to the apparatus tests. The run would then be set by part 1's linters and tree checks, not by pytest, so it would finish perhaps one to two minutes sooner, on about 4 of every 10 pull requests. That is an estimate from summed test time, not a CI measurement.

**Decision needed.** Should a pull request that changes only apparatus files skip every simulator test, and not only the costly ones?

- **Skip them all.** No apparatus file is an input to a simulator test except the root `conftest.py`, which runs inside every test, and `quality.yml`, which says how the suite runs. A change to either that broke a simulator test would most likely break apparatus tests too, which still run. `main`'s push run always runs everything, so a miss shows up on `main` within minutes of the merge, as it does for the item-only fast path.
- **Keep skipping only the costly tests.** Every pull request keeps running the simulator's ordinary tests, so a miss can never reach `main` this way. It costs about a minute more on each such pull request.

**Recommendation:** skip them all. The only inputs the two choices treat differently are the root `conftest.py` and `quality.yml`, and the backstop for both is a run that already happens on every merge. The choice is the owner's because it changes what a pull request proves before it merges.

**Done when.** The decision is recorded here. If it is to skip them all, `--skip-costly` becomes a selection of the apparatus tests by the same rule `tools/workflow_paths_check.py` applies, and the median wall time of apparatus pull requests is measured over at least 20 runs.

**Generator check.** One-off. It is a wider version of one optimisation, and no reader misread a fact.
