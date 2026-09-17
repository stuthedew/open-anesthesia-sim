---
id: PL-WXKD
title: No command answers whether the workflow lane is converging: docket trend reports the workflow/product balance, so a session asked whether accumulation is slowing re-derives filed-per-closed, surface saturation and severity mix by hand at full context
status: untriaged
feature: convergence-visibility
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/plan.py
added: 2026-09-17
---

**Problem.** No command answers whether the workflow lane is converging: docket trend reports the workflow/product balance, so a session asked whether accumulation is slowing re-derives filed-per-closed, surface saturation and severity mix by hand at full context

**Measured 2026-09-17, in answer to "is the accumulation slowing?".** Every
number below came from a throwaway script over `docs/items/`, at full session
context. None of it is reachable from any shipped command, so the next session
asked the same question pays the same cost.

Periods are 7 days anchored at 2026-08-23, the first `added` date. The last is
5 days, so rates are normalised per day where the count is compared.

| period | filed/day | closed/day | filed per closed |
| --- | --- | --- | --- |
| 08-23 | 3.6 | 1.4 | 2.50 |
| 08-30 | 34.3 | 25.0 | 1.37 |
| 09-06 | 15.3 | 11.4 | 1.34 |
| 09-13 | 31.2 | 20.6 | 1.51 |

Rolling 7-day filed-per-closed: 3.00, 1.49, 1.79, 1.58. **Plateaued, not
falling.** This is gross inflow over closures in a window, so it is an upper
bound on `PL-CSHL`'s 0.69, which counts only items attributable to the work on
a given item. The two are not comparable and neither refutes the other.

**Surface saturation** — cumulative distinct apparatus paths named by a filed
item, store paths (`docs/items`, `docs/WORKING_NOTES.md`, `docs/dead-ends.md`)
excluded:

| through | cumulative paths | new that period | filed | new paths per item |
| --- | --- | --- | --- | --- |
| 08-23 | 29 | 29 | 25 | 1.16 |
| 08-30 | 92 | 63 | 240 | 0.26 |
| 09-06 | 114 | 22 | 107 | 0.21 |
| 09-13 | 134 | 20 | 156 | 0.13 |

134 distinct paths against 117 apparatus files in the tree: the surface has
been covered. This is the measure that distinguishes exhaustion from failure,
and it is the one nothing reports.

**Why a raw recurrence rate misleads.** 90% of items filed in the last period
name a path some already-closed item had touched, which reads as fixes not
holding. It is arithmetic: 528 workflow items over 117 files is 4.5 items per
file, so past week two every finding *must* be a return visit. A convergence
report has to pair recurrence with saturation or it will accuse the lane of
regression it has no evidence for.

**Severity decay**, share of each period's workflow filings:

| period | P1 | P2 | P3 | defect | P3 share |
| --- | --- | --- | --- | --- | --- |
| 08-23 | 0 | 19 | 4 | 28% | 17% |
| 08-30 | 2 | 160 | 69 | 52% | 30% |
| 09-06 | 1 | 87 | 19 | 64% | 18% |
| 09-13 | 0 | 82 | 70 | 53% | 46% |

Open workflow backlog: 160 items, 0 P1, 79 P2, 81 P3.

**What the command should report**, at minimum: filed-per-closed rolling;
new-paths-per-item; the P1/P2/P3 mix of filings, not of the backlog; and the
count blocked on an owner decision, which on this date is 33 of 160 open
workflow items and is the binding constraint rather than throughput.

**Care needed on the denominator.** `docs/items` appears in only 65 of 528
workflow items' `touches`, so excluding store paths changes little here — but
it must be excluded explicitly, because the store sits inside `workflow_paths`
and every capture made while doing something else would otherwise count as
apparatus work. `docket trend` already makes this exclusion for churn; the
same rule applies.

**Not a health score.** `docs/dead-ends.md` records open-backlog ratio as
refuted (`PL-03XH`). This reports rates and composition, and must not
reintroduce a single number standing for the lane's health.
