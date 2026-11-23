---
id: PL-7TB2
title: PL-04KR's severity prediction has missed six weeks running, and none of the six readings found an unfound generator: decide whether release keeps printing it
priority: P1
effort: S
status: needs-decision
classes: infra, planning
feature: convergence-visibility
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, docs/items/PL-04KR-pre-register-the-apparatus-convergence.md
deferred-from: v0.7.0 - filed after the gate froze; an apparatus reading of release reports, with no effect on what a learner sees
added: 2026-11-23
filed-pr: 2301
payoff: the release cut stops filing a reading item each week for a signal that has not found a generator, or keeps it on the owner's word
root-cause-of: PL-P6KV, PL-7LMM, PL-40ZB, PL-Z1ZT, PL-NJ54
generator: live - each release whose last complete week holds a workflow filing at P1 prints a miss, and each miss is read as its own item
misread: whether a workflow filing's priority band records how severe an apparatus defect is
---

**Problem.** PL-04KR's severity prediction has missed six weeks running, and none of the six readings found an unfound generator: decide whether release keeps printing it

**Why it matters.** A signal that fires every week without changing a decision costs a reading item each time, and it teaches the cut's reader to skip the line where a real miss would also appear.

**Done when.** The owner's answer is recorded here. Under option 1, `bin/docket release` no longer prints the severity prediction, `subprojects/docket/README.md` says so, and `PL-04KR` records the deviation and its reason. Under option 2, this item closes with the answer and nothing changes.

**What the six readings found.** `bin/docket release` has printed a broken severity prediction for every complete week from 2026-10-12 to 11-22: a workflow-lane filing at `P0` or `P1` whose band neither the generator tier nor an `owner-priority:` record explains. Each week was read, and none of the six readings found a cause that triage's generator check had not already recorded.

1. 2026-10-12: two simulator items counted only because they also named a rule file (`PL-04KR` § "Result"). The reading fixed the count (`PL-00TR`).
2. 2026-10-19: eight filings, three of them the same counting gap, fixed by `PL-NHQ6`. The rest were the owner's defect review, an owner-set band and a three-item line that already had its fix (`PL-P6KV`).
3. 2026-10-26: one gate refusing correct work, a band its own rules give it (`PL-7LMM`).
4. 2026-11-02: twelve, ten from the copy editor the owner asked for, whose heads `PL-HGZS` and `PL-J1ZM` were recorded before the cut, and two from an itemless guard hook review (`PL-40ZB`).
5. 2026-11-09: four, three earned as guard gaps or a gate refusing correct work and one set by the owner's request without a record (`PL-Z1ZT`).
6. 2026-11-16: one rider that took the band of owner-ordered work it unblocked (`PL-NJ54`).

Five reading items so far (`PL-P6KV`, `PL-7LMM`, `PL-40ZB`, `PL-Z1ZT`, `PL-NJ54`), and two of the readings ended by narrowing the count itself. The band records order as well as severity: the generator tier, an owner's order, a `safety` class, a blocker's band and a rider's band all reach `P1` without an apparatus defect being severe. So the count keeps meeting a new kind of band that is not severity, and each costs a reading.

**What the research says.** Google's SRE book, chapter 6, "Monitoring Distributed Systems" (https://sre.google/sre-book/monitoring-distributed-systems/, full chapter read 2026-11-23), asks before keeping an alert rule: "Does this rule detect an otherwise undetected condition that is urgent, actionable, and actively or imminently user-visible?" It says "Every page should be actionable", that "Pages with rote, algorithmic responses should be a red flag", and that rarely exercised alerting configuration "should be up for removal". Here the condition is detected otherwise: triage's generator check recorded every generator these weeks held before a cut printed the miss. Lakens (2024), "When and How to Deviate From a Preregistration", Collabra: Psychology 10(1):117094, doi:10.1525/collabra.117094 (abstract and the first half of the full text read 2026-11-23), names increasing validity as a justified reason to deviate from a preregistered plan, and says a deviation "should not just be reported, but the consequences of the deviation should also be evaluated".

**Decision needed.** Should each release cut keep telling you when a workflow filing reached the top priority band, or stop, keeping the other two signals: new places the workflow is changing, and fixes that did not hold?

1. **Stop printing the severity prediction (recommended).** The cut stays silent about top-band filings, and `bin/docket inflow` still shows each week's filings by priority. The two other predictions keep running, and the change is recorded in `PL-04KR` as a deviation with this item's evidence, as Lakens asks. Cost: a severe apparatus defect is no longer named at the cut. Triage's generator check and the re-entry list are what found every cause these weeks held.
2. **Keep it.** Each week with a top-band filing costs one small reading item, as five have so far, and the readings will keep finding bands that record order rather than severity.

**Recommendation.** Option 1. The signal has fired six weeks running and changed no decision about a generator, which is the test `.claude/rules/apparatus-standard.md` § "A check earns its place every run, or it is retired" sets. It is the owner's call because `PL-04KR` exists so the owner's expectation that workflow inflow falls can fail loudly, and this removes one of the ways it can fail.

**Generator check.** One cause behind five reading items: the severity prediction reads a priority band, and the band records order as well as severity. The decision above is its fix.
