---
id: PL-H9KW
title: quality.yml's pytest step now takes about 9 minutes, about 82% of every checks run, up from 48 s on 2026-09-05 and 144-359 s on 2026-09-28 while test functions grew 29%, so a few slow tests are the likely cause; and the 15-minute timeout's comment still sizes it against a 3m44s job
priority: P2
effort: S
status: ready
classes: infra, test
feature: ci-cost
touches: tests/unit/test_doc_check.py, .github/workflows/quality.yml
added: 2026-10-17
payoff: every pull request's checks run finishes minutes sooner, and its timeout is sized against what the job now takes, so a slow runner reads as slow rather than as a red check
verify: ! grep -qF 'twice the observed 3m44s' .github/workflows/quality.yml
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

**Diagnosed 2026-10-17, after the capture.** CI's exact command run locally
(4 cores, `-n 8 --dist worksteal --cov=anesthesia_sim.core --cov-branch`, with
`--durations=80 --junitxml` and a scratch plugin timestamping each test on its
worker), and the `checks` logs of runs 39002948586 (2026-10-17) and
36359721141 (2026-09-27, push to `main`).

- **Not the runner.** Both CI logs show `created: 8/8 workers` on image
  `ubuntu-24.04`, so the growth is the suite. Items 5,577 to 8,262 (+48%);
  pytest 290 s to 551 s. Two parts: reaching 99% took 186 s then and 323 s now,
  and **99% to 100% took 73 s then and 187 s now**, a tail.
- **Where the work is.** Local run 349 s, 2,249 test-seconds:
  `tests/reference/test_late_washout_against_published_fits.py` 602 (27%);
  `tests/integration/test_controller.py` 323 (14%), of which 278 is three
  *setups*; `tests/unit/test_doc_check.py` 192, of which 150 is
  `test_this_repository_is_clean`,
  `test_this_repository_reports_its_own_resident_total` and
  `test_this_repository_measures_its_own_skill_on_demand`, each analysing the
  whole repository; then `test_coupled_dynamics.py` 137,
  `test_simulation_view.py` 128, `test_published_wash_in_and_elimination.py` 125.
- **What the tail is.** In a 310 s timestamped run, every worker's last tests
  are washout curves (`PL-4Z5Y`'s subject, in flight in another session) or
  `test_a_run_at_the_supported_run_length_offers_no_place_to_branch_where_it_stands`,
  which began at 207 s, built both 24-hour trunks in setup (104 s) and ended the
  run at 310 s.
- **Why the 24-hour trunks cost so much.** `trunk_stepped_onto_the_limit` and
  `trunk_halted_on_a_mark_at_the_limit` (added 2026-10-03 by `PL-5291`, #1317)
  each take 864,000 steps of 0.1 s. They are `scope="module"`, which under
  xdist means once per worker that runs one of their six tests, so the run built
  them three or four times, not twice, and late. A `SimulationController`
  stepped an hour pickles to about 4 KB and unpickles to the same snapshot
  (measured), so it can be shared the way `washout_curve` shares a curve.
- **What these fixes cannot reach.** The bulk to 99% grew roughly with the
  item count and has no single owner, so "under about 4 minutes" below is not
  reachable from them alone; the tail is this item's measurable target.

**Why it matters.** It is most of every `checks` run, on every pull request,
code ones included, and again on each base merge `update-armed.yml` makes. The
job's `timeout-minutes: 15` comment says "15 rather than twice the observed
3m44s"; the slowest runs are now near 11.6 minutes, and `PL-4Z5Y` measured slow
runners at about 1.3-1.4 times fast ones on this step, so the margin is
shrinking. A timeout reads as a red check, and the same check failing twice
stops a session (`CLAUDE.md`).

**Where.** `.github/workflows/quality.yml` (the pytest step and the `checks`
job's timeout comment); whichever test modules the measurement names.

**Generator check.** A one-off (triaged 2026-10-17). The fact is a test's own
CI cost, which nothing records per test, so a slow one is found only when
somebody times the step. But the store's other members are the washout curves
twice over (`PL-F08Y`, done, and `PL-4Z5Y`), so it is one set of tests, not
one fact misread by several readers. No head's `misread:` states it.

**Measured and decided later on 2026-10-17.**

- **Coverage is not a lead.** The same run without `--cov` took 371 s against
  349 s with it, so the tracer is not where the time goes.
- **The trunks go to `PL-4Z5Y`** (project owner, 2026-10-17, ratified, over
  `PL-H9KW` extending `PL-4Z5Y`'s dealing hook in a second pull request after it
  merges). `PL-4Z5Y`'s hook in `tests/reference/conftest.py` deals each washout
  curve's first test to the head of a worksteal slice. It now also deals the six
  tests requesting `trunk_stepped_onto_the_limit` or
  `trunk_halted_on_a_mark_at_the_limit`, back to back at the head of one slice.
  Two reasons: it is the same mechanism in that item's unmerged file, and with
  only the curves dealt the trunk test would still end the run, hiding
  `PL-4Z5Y`'s own gain. That session was told on 2026-10-17 and records it in
  `PL-4Z5Y`.
- **Step 2 below is dropped as a result.** Run back to back at a slice head,
  the six tests build each trunk once per run, at the start: pytest keeps a
  module-scoped fixture alive across consecutive tests from its module, and
  worksteal steals only from a queue's tail (`steal_from.pending[-num_steal:]`
  in pytest-xdist 3.8.0's `xdist/scheduler/worksteal.py`). Sharing the trunk
  across workers would then buy nothing, and would be a second mechanism. This
  is inferred, so a timestamped run after `PL-4Z5Y` merges checks it.
- **Corroborated independently.** The friction-batch session measured the
  same suite (wall 293 s against 240 s perfectly balanced). It found
  `test_controller.py` at 266 s, of which 230 s was three per-worker trunk
  rebuilds (51, 94 and 85 s), and `test_doc_check.py` at 164 s. It suggested
  ordering the whole collection longest-first from a recorded durations file.
  The bound is Graham RL, "Bounds on multiprocessing timing anomalies," SIAM J
  Appl Math 1969;17(2):416-429: LPT is within 4/3 - 1/(3m) of the optimal
  makespan, against 2 - 1/m for an arbitrary list order. Not taken now:
  dealing the two expensive clusters first removes the measured tail without a
  durations file to keep current. Revisit if the 99%-to-100% stretch stays well
  above 73 s after `PL-4Z5Y` merges.
- **One whole-repository `doc_check` analysis is about 59 s**, profiled on
  2026-10-17. A `checks` job runs it five times: the two `doc_check.py check`
  steps in `quality.yml`, plus the three tests below. Within one analysis the
  item store is read seven times, which is filed separately under `ci-cost`.

**Next steps, revised again 2026-10-17.**

1. ~~No-coverage timing~~: done, above.
2. ~~Share each trunk across workers~~: dropped, above.
3. ~~Deal the trunk tests first~~: moved to `PL-4Z5Y`, above.
4. ~~Share one `doc_check` analysis among `test_doc_check.py`'s three
   whole-repository tests~~: done 2026-10-17. They are
   `test_this_repository_is_clean`,
   `test_this_repository_reports_its_own_resident_total` and
   `test_this_repository_measures_its_own_skill_on_demand`. All three now call
   a `functools.cache`-decorated `_this_repository()`, so each process analyses
   the tree once. Measured: the three pass together in 29 s, one 27 s analysis
   and two calls under 5 ms, and the module's 893 tests pass in 63 s.
5. After `PL-4Z5Y` merges: re-time CI against the done-when below, and restate
   the `timeout-minutes: 15` comment against the new measured job time.

**Done when.** On at least five successful CI runs after the change, the
pytest step's 99%-to-100% stretch is back near its late-September 73 s, no
24-hour trunk is built more than once per run, no test is removed or skipped to
get there, and the timeout comment states the job time it was sized against.
The step's median is recorded against the 551 s baseline either way.
