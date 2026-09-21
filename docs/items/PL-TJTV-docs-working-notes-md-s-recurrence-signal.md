---
id: PL-TJTV
title: docs/WORKING_NOTES.md's recurrence-signal thread names the feature as four items and lists PL-TZ7T, but bin/docket feature recurrence-signal holds five and not that one, so the thread's membership list is drifted in both directions
priority: P3
effort: S
status: ready
classes: docs
touches: docs/WORKING_NOTES.md
added: 2026-09-21
payoff: the recurrence-signal thread stops describing a different feature than the store holds, so a session picking it up is not reconciling a membership list the store answers in one command
verify: ! grep -qF ', four items.**' docs/WORKING_NOTES.md
---

**Problem.** docs/WORKING_NOTES.md's recurrence-signal thread names the feature as four items and lists PL-TZ7T, but bin/docket feature recurrence-signal holds five and not that one, so the thread's membership list is drifted in both directions

**Why it matters.** `docs/WORKING_NOTES.md` is where a session reads the
narrative behind an open thread, and this one now describes a different feature
than the store holds. Re-measured 2026-09-21: `bin/docket feature
recurrence-signal` reports **6/6 done (complete)** — `PL-CJ5R`, `PL-DGP0`,
`PL-S6FL`, `PL-THLT`, `PL-X5JR`, `PL-4JHS` — while line 2090 of the notes still
opens "**The feature is `recurrence-signal`, four items.**" and names `PL-TZ7T`,
which the feature does not hold. So the drift is worse than filed: not only is
the membership wrong in both directions, the thread reads as open work when the
feature has closed. A session picking the thread up spends its first minutes
reconciling a list that the store answers in one command.

**Done when.** The `recurrence-signal` thread in `docs/WORKING_NOTES.md` either
names the six items `bin/docket feature recurrence-signal` reports and records
that the feature is complete, or the thread is removed as a thread the store now
answers. `PL-TZ7T`'s absence is stated rather than silently dropped — it was
named in the plan and is not in the feature, and a reader who remembers the plan
needs to know which is right.
