---
id: PL-04KR
title: Pre-register the apparatus-convergence expectation on two causal signals, baselined 2026-09-19, so the owner's expectation that workflow inflow declines can fail loudly rather than be re-argued
priority: P2
effort: M
status: ready
classes: infra, planning
feature: convergence-visibility
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/trend.py, subprojects/docket/tests/test_trend.py, docs/items
added: 2026-09-19
verify: grep -q 'def test_the_re_entry_rate' subprojects/docket/tests/test_trend.py
---

**Problem.** The project owner stated an expectation on 2026-09-19: with the
known generator root causes closed and no new user-requested functionality being
added, the rate of new workflow-lane issues should decline from here. They asked
for a sanity check on it, with the intent stated precisely — "to make sure we
don't need to investigate an unknown issue that is generating additional bugs
that we are just patching other than fixing the upstream issue, or an unknown
generator basically."

Nothing currently answers that. `bin/docket trend` reports closures,
effort-weighting and churn, and **no inflow term at all**, so the command whose
name promises this shows only the lagging half. `PL-WXKD` is the standing item
for the gap.

**What to watch, and what was rejected.** The owner explicitly ruled out backlog
counts and any product-to-workflow ratio — "I don't really care about the backlog
so much and it doesn't help me to say that we have a bunch open still". Two
causal signals instead:

1. **Re-entry rate** — new workflow items landing on a path that a *closed* item
   also touched, where the closure was within the preceding 30 days. Rising means
   fixes are not holding, which is the "patching rather than fixing upstream"
   case. **This is the signal that is currently structurally impossible to see**:
   of 623 attributed parent-child links in the store, 100% of children were filed
   in the very commit that closed the parent, median lag zero, nothing above zero.
   The existing attribution captures filed-while-working and never
   fix-did-not-hold.
2. **Largest unexplained cluster** — open items sharing a mechanism with no
   `root-cause-of:` head above them. Growing means an unfound cause is
   accumulating instances. **27 on 2026-09-19** (`PL-G424`).

Rejected, with reasons: gross inflow ÷ closures, because a capture- or
triage-policy change moves it for reasons unrelated to generators and the
reassuring direction is the one it would show either way; release workflow share
and open-backlog counts, because closures lag generation by weeks — 151 open
items and 44 of 65 generator-explained items still open mean apparatus-heavy
releases continue well after generation falls; and raw path recurrence, which
`PL-WXKD` already refuted as arithmetic rather than regression at 90% on a
surface of 117 apparatus files. The 30-day bound on signal 1 is what
distinguishes it from that refuted metric: "this path came back within 30 days of
us closing something on it" is a statement about a fix, not about surface size.

**The baseline, measured 2026-09-19.** The window 2026-09-17 to 09-19 is
contaminated and excluded: it was a deliberate generator campaign, with six of
the seven recorded generators both recorded and closed on 09-19. Week 1 is also
excluded as the ground-up build period. The clean baseline is weeks 2-4.

```
self-generation rate (workflow lane)   0.696   multiplier 1/(1-r) = 3.29
inflow / closures, weeks 2-4           1.38, 1.54, 1.43   (week 1: 2.40)
new paths per filed item               1.16 -> 0.26 -> 0.21 -> 0.13
P1 workflow filings by week            0, 2, 1, 0
open workflow P1 band                  0
P3 share of workflow filings           17% -> 29% -> 24% -> 41%
largest unexplained cluster            27
re-entry rate                          not yet measurable - see signal 1
```

**The prediction, to be checked at the next three releases.** Re-entry rate flat
or falling once it can be measured; largest unexplained cluster not growing above
its post-sweep value; P1/P2 workflow filings staying at zero; new paths per filed
item staying at or below 0.13. If all hold, the owner's expectation was correct
and no tracking mechanism was needed. If any moves the wrong way, that is the
trigger to investigate, and which one moved says what to look for: re-entry
points at a fragile area, cluster growth at an unnamed cause.

**Two things whoever implements this must not get wrong.** Generator-campaign
filings need breaking out separately, or the next deliberate sweep reads as
regression and sends someone hunting a generator that does not exist — the
contamination this brief already had to exclude by hand. And 11 open items
declare another item's *file* as their `touches`, which would inflate the
re-entry rate for a bookkeeping reason; item-file paths need excluding.

**Staleness caveat on every number above.** `PL-LKGL` measured 32% of the
workflow lane dead or partly overtaken on 2026-09-12. The 151, the cluster sizes
and both rates are therefore upper bounds. The apparatus backlog review
commissioned 2026-09-19 will move them.

**Why it matters.** The expectation is currently unfalsifiable, which is the
worst of both states: it cannot be confirmed, so it gets re-argued from memory
in every session that notices the apparatus lane is busy, and it cannot fail,
so an actual unfound generator would go on producing instances with nothing
saying so. `CLAUDE.md` § "What this project is" settles the *level* question
("there is too much apparatus" stays refused) and says in the same breath that
it cannot settle the *trend* one - "Apparatus inflow should be declining now
that the functionality is settled, and if it is not, something is generating
work we should go and find" is named there as live, and this item is what it
points at. A pre-registered prediction with its numbers fixed before the
outcome is known is the only form that can lose; a measurement chosen
afterwards will agree with whoever chose it.

The half that is genuinely missing rather than merely unpublished is signal 1.
Of 623 attributed parent-child links, 100% of children were filed in the commit
that closed the parent - so the store records filed-while-working and has never
once recorded fix-did-not-hold. That is not a low reading of re-entry; it is no
reading at all, and it is the signal that would distinguish "we are patching
instances" from "we are fixing causes".

**Done when.** A command reports both signals over the store - re-entry rate on
the 30-day bound, and the largest open cluster carrying no `root-cause-of:`
head - with generator-campaign filings broken out separately and item-file
paths excluded from the re-entry surface, which are the two ways the brief
above says the numbers go wrong. The 2026-09-19 baseline in this item is what
the command's output is read against, and the prediction is checked at each of
the next three releases, with the result recorded here. If all four predictions
hold, this item closes having found nothing, which is the outcome it exists to
be able to report.
