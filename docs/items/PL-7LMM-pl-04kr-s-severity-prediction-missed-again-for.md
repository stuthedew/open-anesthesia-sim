---
id: PL-7LMM
title: PL-04KR's severity prediction missed again for 2026-10-26..11-01: bin/docket release at v0.6.14 and v0.6.15 both reported one P1 workflow-lane apparatus filing whose band no rank or owner set, and no item names which filing it is or why it was P1
priority: P2
effort: S
status: done
classes: infra
feature: convergence-visibility
touches: docs/items/PL-7LMM-pl-04kr-s-severity-prediction-missed-again-for.md
added: 2026-11-04
closed: 2026-11-14
pr: 2153
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

**Verdict, read 2026-11-14: a severity the prediction should allow, with no unfound generator behind it, and no restatement needed.**

1. **The band was earned.** `PL-D59R` was a hard gate refusing correct work: close-out's mutation audit could not reach a verdict within its 2-hour bound on a simulator branch that changed a large display test, so the audit could only refuse. `CLAUDE.md` § "Product focus" names a hard gate refusing correct work as one of the three apparatus findings that stop a product session, so `P1` was the band its own rules give it.
2. **No unfound generator.** `PL-P6KV` already read `PL-D59R` as the third member of a line that re-enters `PL-CZXN` (verify's removed check for a removed assertion), beside `PL-7FPD` and `PL-H57W`. All three are closed. `PL-D59R` closed on 2026-10-31 with pull request #1893, and its feature, `verify-false-reject`, is complete (`bin/docket feature verify-false-reject`, 2026-11-14).
3. **No restatement.** `PL-04KR`'s prediction that no workflow-lane filing reaches `P1` exists to bring a reading like this one. Its baseline weeks held 0, 2, 1 and 0 such filings, so one filing a week is inside what the baseline measured, and a rule that left out a gate refusing correct work would need a field recording that reason, which no item carries today. A later miss for that reason is read the same way.
