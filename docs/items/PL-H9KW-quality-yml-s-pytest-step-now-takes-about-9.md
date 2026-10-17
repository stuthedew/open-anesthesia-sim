---
id: PL-H9KW
title: quality.yml's pytest step now takes about 9 minutes, about 82% of every checks run, up from 48 s on 2026-09-05 and 144-359 s on 2026-09-28 while test functions grew 29%, so a few slow tests are the likely cause; and the 15-minute timeout's comment still sizes it against a 3m44s job
status: untriaged
feature: ci-cost
added: 2026-10-17
---

**Problem.** quality.yml's pytest step now takes about 9 minutes, about 82% of every checks run, up from 48 s on 2026-09-05 and 144-359 s on 2026-09-28 while test functions grew 29%, so a few slow tests are the likely cause; and the 15-minute timeout's comment still sizes it against a 3m44s job

**Measured 2026-10-17**, from the Actions API (read-only session, nothing run
locally):

- The pytest step of `quality.yml`'s `checks` job took 9m13s on run
  39002948586 (pull request #1475) and 9m06s on run 38317647549 (push to
  `main`, 2026-10-12), of jobs lasting 11m12s and 11m03s.
- The last 100 completed `quality` runs (2026-10-12 to 2026-10-17): 59
  succeeded, median 548 s on `pull_request` and 620 s on `push`, 90th
  percentile about 695 s. About 190 run-minutes a day, each run rounded up to
  the minute, so roughly 5,700 per 30 days; `get_workflow_run_usage` returns
  0 billable ms, so the billed figure could not be read. The repository is
  private (`PL-SSQX`), so minutes are billed past the plan's allowance.
- History: 48 s for 1,820 tests on 2026-09-05 (`PL-SDHR`); 144-359 s by runner
  class on 2026-09-26 to 09-28 (`PL-4Z5Y`). `def test_` functions under
  `tests/`: 2,286 at the last `main` commit before 2026-09-28, 2,940 now
  (+29%), while the step's time roughly doubled or tripled.
- Largest test additions since 2026-09-28 by `git diff --numstat`: the two
  Markdown spec texts under `tests/unit/markdown-specs/` (about 20,000 lines
  between them), `tests/unit/test_doc_check.py` (+5,094),
  `tests/integration/test_simulation_view.py` (+1,580),
  `tests/integration/test_controller.py` (+1,220). These are leads, not a
  diagnosis: which tests are slow is unmeasured.

**Why it matters.** It is most of every `checks` run, on every pull request,
code ones included, and again on each base merge `update-armed.yml` makes. The
job's `timeout-minutes: 15` comment says "15 rather than twice the observed
3m44s"; the slowest runs are now near 11.6 minutes, and `PL-4Z5Y` measured slow
runners at about 1.3-1.4 times fast ones on this step, so the margin is
shrinking. A timeout reads as a red check, and the same check failing twice
stops a session (`CLAUDE.md`).

**Where.** `.github/workflows/quality.yml` (the pytest step and the `checks`
job's timeout comment); whichever test modules the measurement names.

**Next steps, for the session that starts this.**

1. Measure before changing anything: `uv run pytest -n auto --dist worksteal
   --durations=30 -q` locally, and read the slowest tests and their modules.
   The CI step adds `--cov=anesthesia_sim.core --cov-branch`, so also time one
   run with that flag to see whether coverage tracing is part of the cost.
2. Compare to the per-module cost at the 2026-09-28 base if the top entries
   are not obviously new.
3. Fix the top offenders by cause (a shared per-run cache the way `PL-F08Y` did
   for the washout curves, a narrower parametrization, or moving a spec
   conformance sweep to `drift.yml`), never by deleting coverage a check
   relies on. Spec-conformance and Qt integration tests are the first leads.
4. Restate the timeout comment against the new measured job time.

**Done when.** The pytest step's median over at least five successful CI runs
after the change is back near its late-September level (under about 4
minutes), with no test removed or skipped to get there, and the timeout comment
states the job time it was sized against.
