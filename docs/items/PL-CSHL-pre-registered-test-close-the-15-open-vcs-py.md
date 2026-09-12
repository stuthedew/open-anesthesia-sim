---
id: PL-CSHL
title: Pre-registered test: close the 15 open vcs.py items as one root-cause round and count what they spawn against the cluster's own baseline of 1.05
status: untriaged
feature: parallel-sessions
added: 2026-09-12
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
