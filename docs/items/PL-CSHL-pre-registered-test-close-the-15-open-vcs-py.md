---
id: PL-CSHL
title: Pre-registered test: close the 15 open vcs.py items as one root-cause round and count what they spawn against the cluster's own baseline of 1.05
status: ready
feature: parallel-sessions
priority: P3
effort: S
classes: infra
touches: docs/items
added: 2026-09-12
verify: python3 tools/doc_check.py check && grep -q '^RESULT: N=' docs/items/PL-CSHL-pre-registered-test-close-the-15-open-vcs-py.md
---

**Problem.** Pre-registered test: close the 15 open vcs.py items as one root-cause round and count what they spawn against the cluster's own baseline of 1.05

**Asked for by the project owner, 2026-09-12:** clean up a batch of
high-impact items and see whether the new-item rate falls. This item fixes the
prediction *before* the work, so the result cannot be read back to suit
whatever happens.

**Why this batch and not "high impact" generally.** Measured 2026-09-12 by
tracing the commit that created each item file back to the id its subject leads
with: items whose `touches` name
`subprojects/docket/src/docket/vcs.py` number 53, of which 38 are closed, and
those 38 spawned 40 further items. The cluster's own rate is therefore

```text
r_vcs = 40 / 38 = 1.05      against a whole-lane r = 0.69
```

so it generates *more* work than it closes, and more than any other part of the
lane. It is the right batch on the merits, and it also happens to be the one
with a baseline solid enough to test against - 38 closures, not a guess.

**The prediction, fixed now.** Fifteen items remain open in the cluster.
Closing them as one root-cause round - deciding once what evidence proves a ref
is done, rather than patching fifteen heuristics - should spawn far fewer than
the baseline predicts.

| | |
| --- | --- |
| H0 (no change) | the 15 closures spawn ~15.8 new items |
| Reject H0 at 5%, one-sided | **9 or fewer spawned** |
| Power vs true r = 0.35 | 0.96 |
| Power vs true r = 0.50 | 0.78 |
| Power vs true r = 0.69 | 0.41 |

**What this test can and cannot say.** It detects a halving or better. It
cannot distinguish 1.05 from 0.69, so a marginal improvement will read as no
result - which is the right cut, because a marginal improvement would not
justify restructuring the lane around root-cause rounds anyway.

**The outcome that refutes the theory, stated in advance.** Ten or more spawned
items means root-cause rounds are no better here than patching one at a time,
and the "inference instead of record" account of `r` is wrong or at least not
actionable. That is a real possible result and it is worth knowing.

**Counting rule, fixed now so it is not argued later.** A spawned item is one
whose creating commit's subject leads with an id belonging to this batch -
the same attribution used to compute the baseline, so the two sides are
measured identically. Items captured during the round but attributable to
another id do not count, in either direction.

**Not delegable:** the round itself is `PL-BHVM`'s design question. This item
is only the measurement wrapped around it, and it closes when the count is in
and recorded here.

---

## Un-withdrawn 2026-09-13: the contingency that killed it never happened

The withdrawal above is correct in every particular and wrong in its premise.
It withdrew this test because consolidating the cluster first would remove the
closures the test counts. **The consolidation was then refuted.** The
full-effort pass over the twenty ref-lifecycle items (`PL-BHVM`) had twenty of
twenty come back `unaffected` and all three structure lenses propose zero edges,
so nothing was blocked, nothing was merged, and the fifteen open items are
exactly as they were.

Verified against the store 2026-09-13: 15 open vcs.py items, 38 closed, **no
`blocked-by` on any of them**, and the baseline recomputed from scratch is
unchanged at 40 spawned over 38 closures, `r_vcs = 1.05`.

**The achievable N is 11, not 15.** Four of the fifteen are `needs-decision`
(`PL-7790`, `PL-8M8H`, `PL-B73C`, `PL-F48B`) and a working session cannot close
them without the project owner. Power at the counts that can actually be
reached:

| N closed | H0 expects | reject at 5% on | power vs r=0.50 | power vs r=0.35 |
| --- | --- | --- | --- | --- |
| 15 | 15.8 | <= 9 | 0.78 | 0.96 |
| 11 | 11.6 | <= 5 | 0.53 | 0.81 |
| 9 | 9.5 | <= 4 | 0.53 | 0.79 |

So eleven still calls a halving. Below about nine it stops being worth running
as a test, though the work stays worth doing.

**The batch does not need the experiment to justify it, and that is the point.**
Ten of the eleven `ready` items are entries on v0.5.0's frozen debt gate, so
they are owed before the milestone begins whatever happens to `r`. The
measurement costs one count afterwards. This item therefore proposes no work
that was not already owed - which is the test `PL-27S8` asks of any proposal,
applied here to a proposal of my own.

**Counting rule, unchanged from the withdrawn version and fixed before the
work:** a spawned item is one whose creating commit's subject leads with an id
from the batch, the same attribution that produced the baseline.

**The refuting outcome, stated in advance:** at N=11, six or more spawned means
no detectable improvement, and the "inference instead of record" account of `r`
is not actionable at this scale.

**Where the result goes.** When the batch lands, append a line that starts with
the word RESULT, then a colon, then `N=` and the closure count, followed by the
spawn count and the verdict against the table above. The `verify:` command greps
for that anchored at the start of a line, and this paragraph deliberately
describes the marker rather than spelling it, so the instruction cannot satisfy
the check it describes.

**Why it matters.** `r` is the only number this project has for whether the
workflow lane is self-sustaining, and it is currently a single whole-history
estimate with nothing testing it. The vcs.py cluster is the one place a test is
possible: it has the worst rate in the lane (1.05 against 0.69) and the only
baseline resting on enough closures to test against. If the rate does not move
here it will not move anywhere, and the root-cause account behind `PL-BHVM`
should be abandoned rather than extended.

**Done when.** A `RESULT: N=` line records the closure count, the spawn count
and the verdict, and `docs/WORKING_NOTES.md` carries one sentence on what it
means for the root-cause account - or this item is dropped with a reason if the
batch closes fewer than nine items, at which point the test is underpowered and
saying so is the honest outcome.

