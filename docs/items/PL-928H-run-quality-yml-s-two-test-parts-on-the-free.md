---
id: PL-928H
title: Run quality.yml's two test parts on the free arm64 runner for pull requests and keep x64 for pushes to main, since arm64 took 284 s against x64's 545 s median for the slower part
priority: P3
effort: S
status: done
classes: infra, perf
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-10-20
closed: 2026-10-20
pr: 1703
payoff: a pull request's tests take about 5 minutes on every run instead of about 9 on the 4 in 10 that draw a slow x64 runner
not-delegable: the end state is the runner GitHub assigns to quality.yml's jobs, which no local command can observe
---

**Problem.** `PL-JWBW`'s trial measured `quality.yml`'s two pytest parts on
`ubuntu-24.04-arm` and `ubuntu-latest` five times on 2026-10-20. The slower
part, part 2, took a median 284 s on arm64 and 545 s on x64, because x64 drew
a slow AMD EPYC 7763 in 4 of its 10 jobs. arm64 was also faster than every fast
x64 runner drawn, and its ten jobs all fell within 6% of their part's median.
Every test passed on arm64. `PL-JWBW`'s brief has the table.

**Why it matters.** Every pull request waits for its slower test part. Every
minute of that wait is also a minute in which `main` can move under an armed
pull request.

**Decision needed.** Whether to run the test parts on arm64, and for which events. Moving the parts to arm64 gives up testing each
pull request on x64, the architecture most users' machines have. The
simulator's reference tests guard clinical values, so a floating-point
difference between the two architectures would matter. None appeared in the
trial.

- **A, recommended.** Pull requests run both parts on arm64. Pushes to `main`
  keep x64, through one expression on each part's `runs-on`:
  `${{ github.event_name == 'push' && 'ubuntu-latest' || 'ubuntu-24.04-arm' }}`.
  Every merged change is still tested on x64 minutes after it lands. A
  difference found only on x64 turns `main` red, which `CLAUDE.md` already
  stops a session for. `tools/main_ci_status.py` times `main`'s runs, so its
  `PYTEST_BASELINE_S` stays an x64 figure and needs no re-time.
- **B.** Both events on arm64. x64 is then tested only by `drift.yml`'s
  monthly full run, so an x64-only difference could stand for a month.
- **C.** Stay on x64. Nothing changes, and 4 in 10 runs keep waiting on a slow
  runner.

**Recommendation: A.** It takes the saving on every pull request and still
tests every merge on x64. Reverting one line per part undoes it.

**Done when.** The owner has chosen. For A or B, both parts' `runs-on` name
the chosen runner, `quality.yml`'s comments that state x64 times are restated,
and one pull request's run shows both parts on arm64.

**Generator check.** A follow-up to a measured trial, not a defect: no reader misread a fact.

**Decided** (project owner, 2026-10-20, ratified, option A, over moving both
events to arm64 and over staying on x64). Both parts' `runs-on` now read
`${{ github.event_name == 'push' && 'ubuntu-latest' || 'ubuntu-24.04-arm' }}`,
and `quality.yml`'s timeout comment restates the arm64 times beside the x64
ones. The pull request that carries this change is its first run on arm64.
