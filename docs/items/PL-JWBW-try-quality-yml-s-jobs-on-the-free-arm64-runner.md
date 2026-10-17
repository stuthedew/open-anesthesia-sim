---
id: PL-JWBW
title: Try quality.yml's jobs on the free arm64 runner (ubuntu-24.04-arm) and compare its pytest time with the x64 runners'
priority: P3
effort: S
status: ready
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-10-17
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
