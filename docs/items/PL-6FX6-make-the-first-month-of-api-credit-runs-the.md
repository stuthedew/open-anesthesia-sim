---
id: PL-6FX6
title: Make the first month of API-credit runs the model-evidence trial: run the same five delegable S items on Haiku 5.5 and Sonnet 5.5, and score each by whether bin/docket verify accepts it, review findings, and total_cost_usd, so the delegable tier is chosen on a measurement instead of the 2026-09-19 asymmetry alone
priority: P3
effort: M
status: needs-decision
classes: session-cost, infra
feature: api-credit-runs
touches: tools/headless_worker.py, docs/maintainer.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-19
---

**Problem.** Make the first month of API-credit runs the model-evidence trial: run the same five delegable S items on Haiku 5.5 and Sonnet 5.5, and score each by whether bin/docket verify accepts it, review findings, and total_cost_usd, so the delegable tier is chosen on a measurement instead of the 2026-09-19 asymmetry alone

**Revised design (2026-10-19), decided (project owner, 2026-10-19, ratified, over merging the cheaper runs' work).** As first written, this trial
would merge cheaper-model work into the record, which is the risk that
`PL-2D28` refused. **Recommended:** run each trial item three times, on Opus
5.5, Sonnet 5.5 and Haiku 5.5. Merge only the Opus run. Score the two cheaper
runs against it by whether `bin/docket verify` accepts them, the defects a
review finds in their diffs, and `total_cost_usd`. Nothing cheap reaches
`main`, and the result is the measurement that `PL-2D28` says would reopen
its decision. `PL-G2D4`, the pre-registered Explore miss-rate measurement, is
the same kind of measurement for search. It is priced at about $140 at most,
so the credit could pay for it too once its `v0.7.0` block lifts.

**Checked 2026-10-19.** The owner stated that day that neither a cheaper model
nor a lower effort level is chosen to save cost, even at no cost (project
owner, 2026-10-19; `docs/maintainer.md`). A cheaper delegable tier could now be
adopted only on a measurement that it is no less correct than Opus 5.5. Five
items cannot show that. Recommendation for triage: drop this item, unless the
owner wants the trial for a reason other than choosing a cheaper tier.
`PL-G2D4`, cited above, was dropped on the same day for the same reason.

**Why it matters.** The trial would spend a month of API credit and owner
attention on choosing a cheaper delegable tier. Since the owner's statement
of 2026-10-19 that no cheaper model is chosen to save cost, a cheaper tier
can only be adopted on evidence that it is no less correct than Opus 5.5, and
five items cannot give that evidence. So the trial may now inform no decision.

**Decision needed.** Should this trial still run? The revised design above was
ratified on 2026-10-19, and the owner's statement about cost came the same
day, so this reopens a ratified decision on that new constraint.
**Recommendation: drop it**, with the reason that five items cannot show a
cheaper model is no less correct, so the trial cannot change which model the
workers use. Keep it only if the owner wants the comparison for another
reason, such as learning where cheaper models fail, and then say that reason
here so the trial is scored against it. This is the owner's call because the
design was ratified by them and the credit is theirs.

**Done when.** Either the item is dropped with that reason, or the trial has
run on five items, each scored by `bin/docket verify`, review findings and
`total_cost_usd`, and the scores are recorded here against the reason the
owner gave.

**Generator check.** A one-off, asked for by the owner.
