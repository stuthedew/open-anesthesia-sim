---
id: PL-7LMM
title: PL-04KR's severity prediction missed again for 2026-10-26..11-01: bin/docket release at v0.6.14 and v0.6.15 both reported one P1 workflow-lane apparatus filing whose band no rank or owner set, and no item names which filing it is or why it was P1
priority: P2
effort: S
status: ready
classes: infra
feature: convergence-visibility
touches: docs/items/PL-7LMM-pl-04kr-s-severity-prediction-missed-again-for.md
added: 2026-11-04
payoff: the miss two releases printed for the week of 2026-10-26 is read, so the next cut's misses are not stacked on an unread one
verify: grep -q '^\*\*Verdict' docs/items/PL-7LMM-*.md
---

**Problem.** PL-04KR's severity prediction missed again for 2026-10-26..11-01: bin/docket release at v0.6.14 and v0.6.15 both reported one P1 workflow-lane apparatus filing whose band no rank or owner set, and no item names which filing it is or why it was P1

**Read at triage, 2026-11-04.** These are facts, not the verdict. Running
`_unexpected_band` from `subprojects/docket/src/docket/inflow.py` over the
filings of 2026-10-26 to 11-01 names one item: `PL-D59R` (`verify --self`
cannot accept a simulator branch that changes a large display unit test). It is
a workflow-lane `P1` with no `root-cause-of:` and no `owner-priority:`. Its
brief gives the reason for its band: the mutation audit could only refuse, and
26 of the 87 merges that changed `src/anesthesia_sim/app/` since 2026-09-26
also changed the test file that made it time out.

**Why it matters.** `PL-04KR`'s predictions exist so that apparatus inflow that
stops falling gets investigated. Two release cuts printed this miss, and no
record says whether it is a severity the prediction should allow or a cause
nobody has found. An unread miss lies under the next cut's misses.

**Done when.** The brief records the verdict in a paragraph that opens
`**Verdict`. It says whether `PL-D59R`'s band was a severity the prediction
should allow, such as a hard gate refusing correct work, whether an unfound
generator is behind it, and whether `PL-04KR`'s prediction needs restating.

**Generator check.** One-off. This is a missed reading, not a misread fact.
