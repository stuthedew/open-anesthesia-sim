---
id: PL-4Z5Y
title: The 24-hour washout curves start in the last third of the run, because worksteal deals the washout file to the first worker 522 tests deep, so a slow CI runner waits about 70 s for them after every other test has finished
priority: P2
effort: S
status: ready
classes: infra, test
feature: ci-cost
touches: tests/reference/test_late_washout_against_published_fits.py, tests/reference/conftest.py, tests/conftest.py, tests/unit/test_reference_conftest.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-27
payoff: a slow CI runner's pytest step falls by at least 30 s, and the washout curves stop being the last thing every run waits on
verify: grep -q '^\*\*Trial read, ' docs/items/PL-4Z5Y-the-24-hour-washout-curves-start-in-the-last.md
not-delegable: whether the trial stays is the slow CI runners' median pytest step over at least five runs after it merges, which no command can take beforehand
---

**Problem.** The 24-hour washout curves start in the last third of the run, because worksteal deals the washout file to the first worker 522 tests deep, so a slow CI runner waits about 70 s for them after every other test has finished

**Measured, 2026-09-28.** `PL-F08Y`'s shared cache computes each of the 8
curves once per run, and on CI it took 79 to 90 s off the pytest step, which is
what it claimed. What the file still costs over no file at all differs by
runner, and the difference is one tail.

- **CI, by runner class.** The pytest step of `quality.yml`'s `checks` job,
  from the Actions API, over every successful run created 2026-09-26 to
  2026-09-27 23:52 UTC. Runners differ by about 1.3x on the same tree, and
  `mypy`'s step time tracks pytest's (correlation 0.85 to 0.98 within each
  window), so it sorts runners: fast took 5 s or less over `mypy`, slow 7 s or
  more. Medians, runs in brackets:

  | pytest step | No washout file | File, per-process cache | `PL-F08Y`'s cache |
  | --- | ---: | ---: | ---: |
  | Fast runners | 144 s (9) | 259 s (9) | 169 s (2) |
  | Slow runners | 189 s (13) | 359 s (13) | 280 s (8) |

  So the file still costs about 25 s on a fast runner and about 91 s on a slow
  one. Slow runners were 13 of the 30 runs sampled before the file and 8 of
  the 11 since the fix.
- **Where the slow runners' 91 s goes.** Read from the progress lines' own
  timestamps in the job logs. Two slow runs with the fix reached 98% of the
  tests at 159 and 161 s, close to the 162 to 172 s of the runs before it, and
  then spent 95 and 99 s on the last 2%. Two slow runs with no file spent 14
  and 37 s there. The file's curves are that last 2%.
- **Why they are last, seen directly.** CI's own command (`-n 8 --dist
  worksteal --cov=anesthesia_sim.core --cov-branch`) on a 12-core Mac, with a
  scratch plugin timestamping each washout test on its worker, ran 149.7 s.
  The first washout test started at 96.3 s and every other slow one between
  114.7 and 134.4 s. They ran in parallel, one or two curves per worker, 11 to
  31 s each, and every one of the 8 workers ended the run on washout tests,
  seven of them within 4.2 s of its end.

**Why it happens.** `worksteal` (pytest-xdist 3.8.0, `check_schedule` in
`xdist/scheduler/worksteal.py`) deals the collection out in contiguous slices at
the start - the first 701 of 5,614 tests to the first worker - and an idle
worker steals the tail half of whichever queue is longest. The washout file's
28 tests are collection positions 523 to 550, so the first worker reaches them
only after 522 others, 148 `test_controller.py` and 193
`test_simulation_view.py` integration tests among them. Nobody steals them
sooner either, because stealing starts only as other slices run dry. So the
curves begin when the rest of the suite is nearly done, and the run waits a
curve or two for them - longer on a slow runner, where each curve is slower and
8 workers share 4 vCPUs. `PL-F08Y`'s brief named the risk before it was built:
whether the curves run in parallel "depends on where `worksteal` put their
tests". They do run in parallel. They start late.

**Why it matters.** About 70 s on every slow-runner `checks` run, most of the
91 s the file still costs there, and a smaller tail elsewhere. For the rest,
`PL-F08Y`'s own case applies unchanged: `main` refuses a branch that is not up
to date, so every minute of `checks` is also a minute for `main` to move under
an armed pull request.

**Done when.** [superseded 2026-10-17: the suite has grown from 5,614 tests
to 8,265 since, so the 280 s and 240 s below no longer describe it; the
trial's own bar, a fall of at least 30 s, is the one that holds.] On at least five slow-runner runs, the median pytest step is 240
s or less, against 280 s now. Each curve is still computed once per run, and no
assertion, tolerance band or step in the file changes. 240 s is the no-file
baseline, 189 s, plus about what the 8 curves' own CPU must add on 4 vCPUs.
That allowance comes from 15 s per curve with coverage on at full speed on the
Mac, measured, and a slow runner's core at about 1.4x the Mac's, assumed rather
than measured.

**Candidate approaches.**

1. **Deal the curves out first.** A `pytest_collection_modifyitems` hook in
   `tests/reference/conftest.py` moves the first test to read each curve to the
   head of a different worker's first slice, computed the way `worksteal` deals
   them, from `config.workerinput["workercount"]` on a worker. Every curve then
   starts near the start of the run, in the worker's own process, so coverage
   sees it as now, and every other washout test reads it from the cache.
   - Cost: about 40 lines, plus a function in the test module saying which
     curves each test reads.
   - Eight tests run apart from their module.
   - It depends on how `worksteal` deals its first slices, which is an xdist
     internal. If that changes, the hook stops helping, but it breaks nothing.
2. **Compute the curves in background processes**, started as the first worker
   finishes collecting, each holding its curve's lock while the tests run.
   - It does not depend on the scheduler.
   - It adds process management.
   - It moves the curves' core lines outside coverage's measurement, so the
     100% `core/` gate has to be checked first.
3. **Make each curve cheaper.** This is `PL-F08Y`'s candidate (3): profile one
   curve's 882,000 `advance()` calls. It is a core change under the
   safety-critical standard, and an item of its own.
4. **Accept the tail.**

[superseded 2026-09-28: answered below] **Decision needed, and recommended:
(1).** It is the only approach that removes the tail without leaving the
worker's process, and if it fails, the only cost is the lost speed. It is the
owner's call because it adds a scheduling hook tied to an xdist internal, for
roughly 40 to 70 s on a slow runner and little on a fast one. It is worth
building only if it saves at least 30 s at the slow runners' median. Measure it
the way the table above was measured, within a runner class, because an
unclassed median moves with the runner mix.

**Answered 2026-09-28: build (1) as a trial** (project owner, 2026-09-28,
ratified, over accepting the tail). Keep it only if the slow runners' median
pytest step falls by at least 30 s, over at least five slow-runner runs after
it merges. If it does not, revert it and record the numbers here.

**How the CI table was taken, to repeat it for the trial.**

- **Runs.** `gh api
  'repos/stuthedew/open-anesthesia-sim/actions/workflows/quality.yml/runs?per_page=100&created=>=DATE'`,
  then each run's `actions/runs/ID/jobs`. In the `checks` job, the pytest step
  is the one whose name starts `Run uv run pytest -n`. Its time is
  `completed_at` minus `started_at`, on successful runs only.
- **Runner class.** The same job's step starting `Run uv run mypy`: 5 s or less
  is fast, 7 s or more is slow.
- **Which tree a run tested.** A push run tests its `head_sha`, placed with
  `git merge-base --is-ancestor`. A pull-request run tests the merge with
  `main`, so it is placed by its `created_at` against the change's merge time.
- **The tail.** `gh run view RUN --job JOB --log`, reading the timestamps of the
  progress lines ending in a percentage, counted from the `created: 8/8
  workers` line.
- **Which worker ran each washout test locally.** A scratch plugin passed with
  `-p` appends `time.time()`, `PYTEST_XDIST_WORKER` and the node id from
  `pytest_runtest_logstart` and `pytest_runtest_logfinish`.

**Built 2026-10-17, as the trial, and slower here.** The hook is built and
working. It makes this container's run slower, not faster, because the curves
were no longer the only tail: `PL-K5VM`'s 24-hour controller builds take over
the tail, and the dealing makes them longer.

- **What was built.**
  - `tests/reference/conftest.py`'s `pytest_collection_modifyitems` takes
    each curve's first reader, longest curve first, and moves it to the head
    of the slice with the least to compute so far. Slice sizes come from
    `first_slice_sizes`.
  - `CURVES_READ`, in the test module, says which curves each test reads,
    in order. The metabolism test now reads its sink curve first, since
    nothing else reads that curve. No assertion, tolerance band or step
    changed.
  - `tests/unit/test_reference_conftest.py` holds `first_slice_sizes` to
    the installed `WorkStealingScheduling`.
  - A worker cannot see the `--dist` mode itself: xdist's `setup_config`
    sets its `config.option.dist` to `no`. So `tests/conftest.py`'s
    `pytest_configure_node` passes the mode in `workerinput`. The first
    hook-on run was missing this, never dealt, and counts as the second
    baseline below.
- **Measured here.** CI's own pytest command, 8 workers on 4 vCPUs, with
  each test timestamped per worker by the scratch plugin described above:

  | Run | Run length | 98% done | Washout tests first start | 24-h controller builds |
  | --- | ---: | ---: | ---: | ---: |
  | No hook | 311.2 s | 188.1 s | 89 s | 4 |
  | No hook | 316.6 s | 187.4 s | 89 s | 4 |
  | Hook | 339.6 s | 232.3 s | 25.6 s | 6 |
  | Hook, rest reordered | 354.1 s | 274.3 s | 25.1 s | 7 |

  The last row had the rest of the collection reordered by a second scratch
  plugin, meant to deal every test of 10 s or more first. It ran before the
  hook instead of after it, so this row is a hook-on run whose slices differ
  from CI's. It is not a replicate, and it is not the heavier dealing it
  was meant to test.
- **What the hook did.** All 8 workers opened on a different 24-hour curve
  at 25.6 s, and the last curve finished by about 95 s. In the baseline they
  ran from 89 s to 301 s. So the washout tail is gone. In its place is
  `test_controller.py`'s six supported-run-length tests and their two
  module-scoped 24-hour builds. The hook shifts the slice boundaries, and
  stealing then splits those six tests over three or four workers, each of
  which rebuilds what it needs. The tables are in `PL-K5VM`.
- **CI before-figure, not yet taken.** Only 5 successful `quality.yml` runs
  have come since 2026-10-15: fast runners at 258, 269 and 286 s, one slow
  run (39002948586) at 553 s, and one unclassed at 376 s. One slow run is no
  median. Whoever takes the reading pulls at least five slow-runner runs
  from before the merge and five from after, the way the CI table above was
  taken.

**Decision needed, and recommended: hold the trial until `PL-K5VM` lands, and
do not run it on CI now.** On this tree the hook is slower in both hook-on
runs, by 23 to 43 s, so the keep criterion of a fall of at least 30 s would
likely fail. That would cost at least five slow-runner runs plus a revert pull
request. Holding means:

1. Status goes to `blocked`, `blocked-by: PL-K5VM`.
2. This branch reverts the hook, its unit test, `tests/conftest.py`'s
   `pytest_configure_node`, the `CURVES_READ` table, the metabolism test's
   reordering and the `docket.toml` entry, then lands only this record. The
   code comes back from the pull request's head ref, commit `8eb2e974`.
3. Once the controller builds are shared, one run without the hook and one
   with it, on the same command, decide whether the CI trial runs at all.

The other route is to run the trial on CI now, as decided 2026-09-28.
Nothing measured here says it would pass.
