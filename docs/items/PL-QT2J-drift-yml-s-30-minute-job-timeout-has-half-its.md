---
id: PL-QT2J
title: drift.yml's 30-minute job timeout has half its margin left: the interpreter job's pytest step took 14.6 min on 2026-10-18, against 3.8 min on 2026-10-01, as the suite grew from 5,463 to 9,354 tests
priority: P3
effort: S
status: ready
classes: infra
feature: drift-visibility
touches: .github/workflows/drift.yml, docs/items/PL-QT2J-drift-yml-s-30-minute-job-timeout-has-half-its.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-18 triage pass
added: 2026-10-18
payoff: the monthly drift jobs keep a timeout that only a hang can reach, so they do not start failing on the suite's growth and reporting weather instead of drift
verify: grep -qE '^\*\*Timed 2026-[0-9-]+\.\*\*' docs/items/PL-QT2J-drift-yml-s-30-minute-job-timeout-has-half-its.md
---

**Problem.** Each `drift.yml` job has `timeout-minutes: 30`. The comment says
the limit sits "past any plausible honest run", because it bounds a hang and
not slowness (`PL-FSH9`). The measurements no longer support "past any
plausible" by a wide margin:

| Run | Date | Job | Tests | pytest step |
| --- | --- | --- | --- | --- |
| 36822855719 | 2026-10-01 | interpreter | 5,463 | 3 min 50 s |
| 39157643905 | 2026-10-18 | dependencies | 9,354 | 9 min 28 s |
| 39157643905 | 2026-10-18 | order | 9,354 | about 7 min 30 s |
| 39157643905 | 2026-10-18 | interpreter | 9,354 | 14 min 35 s |

The interpreter job spent about 5 minutes before the first test finished:
about 2 minutes before pytest printed its header, and about 3.3 minutes from
there to the first dot. The other jobs did not. All jobs run `-n auto`, which
gives 4 workers on a 4-vCPU runner, while `quality.yml` runs twice as many
workers as CPUs.

**Why it matters.** The suite grew 71% in 17 days. At that rate, the
interpreter job would pass 30 minutes within about a month, and then fail
every month on a timeout that says nothing about drift. That is the same
weather-not-news failure that `PL-FPCK` fixed.

**What to find out.** First, why the interpreter job starts 5 minutes later
than the other two jobs. It uses the runner's toolcache CPython instead of a
uv-managed one, so bytecode compilation on first import is a candidate.
Second, whether `quality.yml`'s worker count, twice the CPU count, shortens
these jobs as much as it shortens `quality.yml`. Measure both before
changing the limit.

**Triaged 2026-10-18.** Run 39157643905 was dispatched on a branch and
tested CPython 3.14.8 from the runner's toolcache, not 3.15. Its `interpreter`
job printed pytest's header 2 min 4 s after the step started and the first
line of dots 3 min 20 s after that. The `dependencies` job ran the same suite
on the 3.14 interpreter uv chose from `.python-version` in 9 min 29 s. So the
slow start is not 3.15's. The toolcache interpreter is the likely cause, which
is inferred and not yet measured.

**Done when.** The cause of the `interpreter` job's slow start, and the effect
of running twice as many workers as CPUs, are each measured on runs dispatched
from a branch. The result and the timeout it leads to are recorded in this
item under a paragraph that opens `**Timed DATE.**`, and `drift.yml` is changed
where the measurement calls for it.

**Generator check.** One-off. It is a margin the suite's growth used up, not a
fact any item misread.
