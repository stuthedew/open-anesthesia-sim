---
id: PL-JWBW
title: Try quality.yml's jobs on the free arm64 runner (ubuntu-24.04-arm) and compare its pytest time with the x64 runners'
priority: P3
effort: S
status: done
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-10-17
closed: 2026-10-20
pr: 1703
payoff: it is known whether the free arm64 runners avoid the slow x64 ones, which take 1.9 times as long
not-delegable: the end state is a measurement of CI runs on GitHub, which no local command can take
---

**Tabled** (project owner, 2026-10-17: "I want low hanging fruit. Not a new
headache to trouble shoot for two minutes savings"). Its payoff is unknown and it risks floating-point differences in the reference tests. Pick it up only if
CI time becomes a problem again.

**Problem.** About 63% of the x64 runners `quality.yml` drew on 2026-10-17
were slow ones, which took 1.9 times as long over pytest (506 s against
263 s). GitHub's Linux arm64 runners, `ubuntu-24.04-arm`, are free on a public
repository and have the same 4 vCPUs
(https://docs.github.com/en/actions/reference/runners/github-hosted-runners,
read 2026-10-17). The PySide6 entry in `uv.lock` has an aarch64 wheel. Nobody
has run the suite on one, so whether arm64 avoids the slow runners is unknown.

**Why it matters.** Even after `PL-T9X9`'s split, a run waits for its slower
part, and at least one part lands on a slow runner in most runs. A runner
class without the slow machines would shorten most runs further, at no cost.

**Risk.** Floating-point results can differ between x64 and arm64, for
example through a different maths library or fused multiply-add in a numpy
build. A reference test with a tight tolerance could then fail. Such a
difference has to be understood before anything moves, not hidden by a looser
tolerance.

**Done when.** The suite has run on `ubuntu-24.04-arm` at least five times, on
a branch or by `workflow_dispatch`. Its pytest times are compared with the x64
slow and fast medians, every test that fails there is understood, and the
result decides whether `quality.yml`'s parts move to arm64.

**Generator check.** A trial the owner agreed to file, not a defect: no reader misread a fact.

**Taken up again** (project owner, 2026-10-20, naming the item).

**Result, measured 2026-10-20.** A temporary workflow ran `quality.yml`'s two
pytest commands, unchanged, on `ubuntu-24.04-arm` and on `ubuntu-latest` in
the same run, and printed each runner's CPU. It ran five times
(https://github.com/stuthedew/open-anesthesia-sim/actions/runs/39371908932,
attempts 1 to 5) and was deleted before the branch merged. Each figure below is
the pytest step's time.

| Runner | CPU | Part 1 | Part 2 |
| --- | --- | --- | --- |
| arm64, all 10 jobs | Neoverse-N2 (2 of 10 logs read) | 134-144 s, median 138 s | 274-290 s, median 284 s |
| x64, slow | AMD EPYC 7763 | 268 s (1 job) | 545-553 s, median 550 s (3 jobs) |
| x64, fast | AMD EPYC 9V45 | 148-156 s, median 153 s (4 jobs) | none drawn |
| x64, fast | AMD EPYC 9V74 | none drawn | 384 s (1 job) |
| x64, fast | Intel Xeon Platinum 8573C | none drawn | 449 s (1 job) |

- **arm64 avoids the slow runners.** All ten arm64 jobs fell within 6% of
  their part's median. The x64 runner drew an EPYC 7763 in 4 of its 10 jobs.
- **arm64 is faster than x64's fast runners too.** Part 1 took 138 s against
  153 s on the EPYC 9V45. Part 2 took 284 s against 384 s and 449 s on the two
  fast x64 runners drawn.
- **A run waits for its slower part, which is part 2.** That part's median was
  284 s on arm64 and 545 s on x64 over these five runs, 4.4 minutes less.
- **Every test passed on arm64**, the reference tests included, so no
  floating-point difference reached a tolerance. The first attempt failed on
  both architectures alike: the trial's checkout was shallow, and the
  `tests/unit/test_headless_worker.py` tests that clone the repository need
  full history. `quality.yml` already fetches it with `fetch-depth: 0`, so the
  trial's second commit fixed it there too. That run is left out of the table.
- `uv sync --locked --dev` installed every dependency on arm64, PySide6
  included.

**What it decides.** Moving the parts is a separate change, because it gives
up x64 testing on each pull request. It is filed as `PL-928H`,
which runs the parts on arm64 for pull requests, with
the recommendation in its brief.
