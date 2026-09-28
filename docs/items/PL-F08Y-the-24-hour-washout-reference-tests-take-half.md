---
id: PL-F08Y
title: The 24-hour washout reference tests take half the suite's wall time: their 8 distinct 864,000-step curves are recomputed in each xdist worker that needs one, adding about 2.5 minutes to every CI checks run
priority: P2
effort: S
status: done
classes: infra, test
feature: ci-cost
milestone: v0.5.17
touches: tests/reference/test_late_washout_against_published_fits.py
added: 2026-09-27
closed: 2026-09-27
pr: 1214
payoff: every checks run and every local make check finishes about a minute and a half sooner - 262.9 s to 168.8 s cold on four cores - with the washout science tests unchanged
verify: grep -q 'fcntl.flock(lock, fcntl.LOCK_EX)' tests/reference/test_late_washout_against_published_fits.py
---

**Problem.** The 24-hour washout reference tests take half the suite's wall time: their 8 distinct 864,000-step curves are recomputed in each xdist worker that needs one, adding about 2.5 minutes to every CI checks run

**Measured, 2026-09-27.** On one 4-vCPU machine, `uv run pytest -n 8 --dist
worksteal --cov=anesthesia_sim.core --cov-branch` with every `__pycache__`
cleared first, as CI starts: `main` at `520e1c74` took 305.4 s, and 149.0 s
with `--ignore=tests/reference/test_late_washout_against_published_fits.py`.
The file's 28 tests cost 156 s of wall time. The ~900 tests added since
`3eaea1cb` (2026-09-24, 146.4 s) cost about 3 s together. The file's 16
slowest tests took 845 s of worker time, the longest 102 s; the slowest test
outside the file takes 29 s. On CI, the median `checks` job went from 4m20s
over seven pull requests merged 2026-09-27 before `PL-KK1Q` (#1134, #1164,
#1166, #1169, #1171, #1176, #1178) to 6m49s over five after it (#1179, #1181,
#1184, #1189, #1201). `PL-KK1Q` recorded "28 tests, about 65 s on four
workers" for the file alone. `PL-0MLZ`'s bytecode change landed in the same
window and is not the cause: with its two lines neutralized, the same run
took 304.3 s.

**Why it happens.** `_washout_curve` runs the gate's 30-minute wash-in and
then 24 hours at the shipped 0.1 s step, 864,000 steps, about 35-50 s per
curve on that machine. The file needs 8 distinct curves: 3 agents x 2
conditions, plus sevoflurane with the hepatic sink in both conditions. Its
`@functools.cache` is per process, and xdist runs 8 worker processes, so a
worker that runs a test needing a curve another worker already has computes
it again. The run above did about 16 curve computations where 8 would do.
xdist 3.8.0's `worksteal` hands each worker a contiguous slice of the
collection (`scheduler/worksteal.py`, `_send_tests`). An idle worker steals
the tail half of the busiest queue (`pending[-num_steal:]`). So a file of
long tests starts on one or two workers, and what stays at the head of that
queue runs there in series, at the end of the run.

**Why it matters.** Every pull request's required `checks` run waits about
2.5 minutes longer, and so does every local `pytest`/`make check` in a
session. `main` refuses a branch that is not up to date, so a longer run also
leaves more time for `main` to move under an armed pull request, and
`update-armed.yml` then re-runs it in full. A science test this expensive
also invites a later session to mark it slow or thin it out. The
safety-critical standard forbids that, and making the file cheap is what
protects it.

**Done when.** Each of the 8 distinct curves is computed once per pytest
run, whatever the worker count, and a cold local 8-worker run of the suite is
reported beside the same run with the file ignored, before and after. Every
assertion, tolerance band and the 0.1 s step in the file stay as they are.

**Candidate approaches, to measure rather than assume.** (1) An
`xdist_group` mark per curve with `--dist loadgroup`. This is the only route
that both computes each curve once and puts different curves on different
workers. It changes the scheduler suite-wide: the `Makefile`, `quality.yml`
and `drift.yml` pytest lines move together, since `tools/doc_check.py`'s
`check_coverage_gate` compares the first two. It also needs a measurement
that the other ~5,400 tests, each its own scope under `loadgroup`, run no
slower than under `worksteal`. (2) A per-run cache shared across workers:
a session fixture computes a missing curve under a lock in the run's
`basetemp`, and the other workers read it. It stays inside
`tests/reference/`, but whether the curves then run in parallel depends on
where `worksteal` put their tests. A cache that dies with the run cannot
serve a stale build, so `PL-0MLZ`'s hazard does not arise. (3) A cheaper
step loop, found by profiling one curve. That is a core change under the
safety standard and would be an item of its own. Recommendation: measure (1)
first, and fall back to (2) if `loadgroup` slows the rest of the suite
(project owner, 2026-09-27, ratified, over leading with (2), the cache that
keeps the change inside `tests/reference/`).

**Done, 2026-09-27: (2), the shared cache, because (1) slowed the rest of
the suite.** The session fixture `washout_curve` hands each test its curve.
The first xdist worker to need a curve computes it while holding an `flock` on
that curve, and publishes it, pickled, into the run's own base temporary
directory. A worker needing the same curve meanwhile waits on the lock and
reads what was published. Without xdist, and on Windows, which has no
`fcntl`, the per-process cache is used as before. No assertion, tolerance
band or step changed.

Measured on one 4-vCPU machine, cold, `-n 8 --cov=anesthesia_sim.core
--cov-branch`, two runs of each at `main` plus the claim:

| | Whole suite | File ignored | Curves computed |
| --- | ---: | ---: | ---: |
| `worksteal`, before | 264.9, 260.9 s | 150.3, 140.1 s | 18 |
| (1) `loadgroup`, one `xdist_group` per curve | 195.9, 179.9 s | 158.3, 150.8 s | 8 |
| (2) shared cache, `worksteal` | 167.2, 170.5 s | no code changed | 8 |

- (1) computed each curve once and slowed the ungrouped tests by 8.0 and
  10.7 s in two back-to-back pairs, which is the condition the ratified route
  falls back on. (2) then measured 19 s faster than (1) in total as well, so
  the fallback was taken without reopening the decision. The likely reason,
  from the durations, is that `loadgroup` deals ungrouped tests out one at a
  time, so a module's tests spread across all eight workers and each of its
  per-process caches is paid on more of them (`PL-ZNPQ`).
- (1) could only make six groups: the one test that reads a sevoflurane run
  with the hepatic sink also reads the run without it, so those two curves
  shared a group and ran in series on one worker. (2) has no such coupling.
- One curve takes 17.3 s alone on one core. Each curve was computed exactly
  once at 8 workers, at 3 (the file alone, 82.1 s) and with xdist off (the
  file alone, 131.2 s), counted by a line each computation appended to a file
  from a scratch copy of the module.
- The file's cost fell from about 118 s to about 24 s, and the suite's mean
  from 262.9 s to 168.8 s, 36%. The runs with the file ignored exercise no
  code this change touched, so the before figures stand for after.
- The `Makefile`, `quality.yml` and `drift.yml` pytest lines are unchanged,
  since the scheduler is.
- Every timing run also failed the two `--discover` tests in
  `tests/unit/test_pr_title_check.py`, a fault of the scratch clone's
  local-path `origin` rather than of this change (`PL-Y4NS`).
