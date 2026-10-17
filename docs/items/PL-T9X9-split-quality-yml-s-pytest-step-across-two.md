---
id: PL-T9X9
title: Split quality.yml's pytest step across two GitHub-hosted jobs, so a slow runner's checks job falls from about 10 minutes to about 6
priority: P2
effort: M
status: needs-decision
classes: infra
feature: ci-cost
touches: .github/workflows/quality.yml, tools/required_checks_check.py, tools/doc_check.py, tests/conftest.py, Makefile
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-10-17
payoff: a slow runner's checks run takes about 6 minutes instead of about 10, so every pull request waits less and main moves less under an armed one
---

**Problem.** Split quality.yml's pytest step across two GitHub-hosted jobs, so a slow runner's checks job falls from about 10 minutes to about 6

**Why it matters.** The pytest step is most of every `checks` run, and
reordering the tests cannot shorten it much. On 2026-10-17 the slow runners'
median pytest step was 506 s of a 621 s job, and fast runners took 263 s of
352 s (`PL-H9KW`'s re-time). `PL-4Z5Y`'s CI reading suggests why reordering
helps little: CI runs 8 workers on 4 vCPUs, so the CPUs are busy for most of
the run. That explanation is inferred, not verified. Spreading the work over
more machines is the change that does not depend on it. Every minute of
`checks` is also a minute in which `main` can move under an armed pull
request, since `main` refuses a branch that is not up to date.

**Raised 2026-10-17** (project owner, 2026-10-17, ratified, "agree with recs",
over a self-hosted runner on the owner's UGREEN DXP2800 NAS). The owner asked
whether part of CI could run in parallel on a personal runner for their own
pull requests. That route was refused for four reasons:

- A fork pull request runs the workflow from its own merge commit, so a rule in
  the workflow file cannot keep outsiders off the runner. Only the repository
  setting that requires approval for outside contributors does.
- A job sent to a self-hosted runner waits for that runner and never falls back
  to a GitHub-hosted one. It fails after 24 hours in the queue.
- The NAS's low-power CPU would likely make its share the slowest one.
- The runner needs upkeep: OS updates, runner updates and disk cleanup.

GitHub's secure-use reference advises against self-hosted runners on public
repositories.

**Proposed design.**

1. Two pytest shards, each in its own job on `ubuntu-latest`. Standard runners
   are free and unlimited on a public repository.
2. Each shard runs `-n cpu_count*2 --dist worksteal --cov=anesthesia_sim.core
   --cov-branch` with no `--cov-fail-under`, and uploads its `.coverage` data
   as an artifact.
3. A final job downloads both, runs `coverage combine`, and fails under 100%.
   This keeps the `core/` gate whole.
4. The split balances expected time, not test count. The 8 washout curves and
   the two controller trunks are the heavy units that `tests/conftest.py`'s
   `deal()` already costs, so the split can reuse those units. The rest can go
   by count or by recorded durations.
5. The shard that also runs the floor section, the linters and `mypy` takes
   about 115 s of other work on a slow runner, so the other shard gets the
   larger share of tests.

**Estimate, not measured.** On a slow runner, half of the 506 s plus each
job's setup gives roughly 340 s per shard job, so `checks` would take about 6
minutes instead of about 10. Each shard draws its own runner, and the run waits
for the slower one. With about 63% of runners slow (19 of 30 after-runs in
`PL-4Z5Y`'s reading), at least one shard lands on a slow runner in about 86% of
runs. The estimate already assumes a slow runner for that reason.

**Costs.**

- **The required check `checks` must still report, and must not pass on a
  skip.** A job skipped because a job it needs failed reports "Success" and
  does not block a merge, even when it is required
  (https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions).
  So the job named `checks` must run `if: always()` and fail unless every job
  it needs succeeded.
- **New job names meet `tools/required_checks_check.py`.** It fails on a job
  that reports on `pull_request` and that nothing requires. Either the owner
  adds the new names to branch protection, or the check learns which jobs the
  `checks` job already gates.
- **`tools/doc_check.py`'s `check_coverage_gate`** compares the Makefile's
  pytest line with CI's. The CI side becomes two shard lines and a combine
  step, so the check must change with it.
- **Twice the runner slots per push.** The Free plan allows 20 concurrent
  jobs (https://docs.github.com/en/actions/reference/limits). The peak seen on
  2026-10-17 was 7 runs at once, so 14 jobs.
- **Each job repeats checkout, the `libegl1` install and `uv sync`.** This
  costs about 20 s, not the 60 s first guessed. On the 19 successful
  slow-runner runs after #1487, the medians were 4.5 s for checkout, 9 s for
  the `libegl1` install, 3 s for `setup-uv` and 1 s for `uv sync`.
- **`tools/main_ci_status.py`'s pytest drift line (`PL-YY32`) reads one
  pytest step in the `checks` job.** After the split there are two steps in
  other jobs, so the line must sum them, and its 470 s baseline must be
  measured again.

**Research before building, 2026-10-17.** The owner asked whether splitting
pytest is the right lever before it is built. The usual levers, checked
against this job:

- **Caching and setup.** Already done. All setup together is about 20 s of a
  621 s slow-runner job (the step medians above).
- **A cheaper coverage tracer.** Already in effect. coverage.py 7.15.4 on
  Python 3.14 uses the `sys.monitoring` core by default, which `Coverage.sys_info()`
  reports as `SysMonitor`. coverage.py's own `doc/config.rst` says that core is
  "the default in Python 3.14+". Measured in a 4-core container with CI's
  pytest command, one run each: 294 s with `--cov` and 299 s without. So
  coverage costs nothing measurable.
- **Parallel work on one runner.** Already done: 8 xdist workers on 4 vCPUs.
- **The slowest tests.** The 8 washout curves took 49 to 57 s each and the
  two controller trunks 99 s and 61 s, on 8 workers sharing 4 cores. Removing
  those 46 tests cut the local run from 294 s to 229 s, 22% less. `core/`
  coverage stayed at 100% of statements and branches without them.
- **Running only the tests a change can affect** (test selection, as in Memon
  et al., "Taming Google-Scale Continuous Testing", ICSE-SEIP 2017,
  https://doi.org/10.1109/ICSE-SEIP.2017.16). Of the 113 merges to `main` from
  2026-10-10 to 2026-10-17, 89 touched none of `src/`, `app/`,
  `tests/reference/` or `tests/integration/`. Skipping the 46 long tests on
  those pull requests would save roughly 110 s per slow run, scaling the 22%
  to the 506 s step. That is an estimate, not a measurement.
- **Faster runners.** Linux arm64 runners (`ubuntu-24.04-arm`) are free on a
  public repository and have the same 4 vCPU as x64 ones
  (https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
  The PySide6 lock entry has an aarch64 wheel. Nobody has run the suite on one,
  so whether arm64 avoids the slow x64 runners, which take 1.9 times as long,
  is unknown.
- **Splitting across runners**, this item. It is the only lever left inside
  the job that cuts every run's time by more than a fifth.

So splitting is still the main lever. Test selection and an arm64 trial are
separate, smaller changes that can follow it.

**Decision needed, and recommended: build it.** `PL-4Z5Y`'s A/B is now
scored, so building the split no longer changes the layout under an unread
trial. The other route is to leave CI as one job and accept about 10 minutes
per slow run.

**Done when.** `quality.yml` runs pytest in two shard jobs and a combining job
named `checks` that holds `core/` at 100%. Across at least five slow-runner
runs, the median `checks` run takes at least 3 minutes less than the 621 s
measured on 2026-10-17.

**Generator check.** Work the owner asked for, not a defect: no reader
misread a fact. The CI suite grew and one job carries all of it, which is a
capacity choice rather than a mechanism producing items.
