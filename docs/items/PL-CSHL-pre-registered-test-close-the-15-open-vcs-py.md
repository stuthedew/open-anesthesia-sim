---
id: PL-CSHL
title: No decisive test of the new-item rate is available at this data volume, and the reasons are worth recording so it is not re-derived
status: untriaged
feature: parallel-sessions
added: 2026-09-12
---

**Problem.** No decisive test of the new-item rate is available at this data volume, and the reasons are worth recording so it is not re-derived

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

## Withdrawn 2026-09-12, before any work was done against it

The project owner asked to consolidate the cluster *before* running the batch,
which is right on the merits and is what broke this design. Recording both the
break and the failed rescue, so the next session does not rebuild either.

**Why consolidating first invalidates the test above.** Its H0 is denominated
per *item closed*. Consolidation removes exactly the closures it counts:

| 15 open items collapse to | reject on | power vs a halving |
| --- | --- | --- |
| 15 (no consolidation) | <= 9 | 0.96 |
| 10 | <= 4 | 0.73 |
| 5 | <= 1 | 0.48 |

**Why re-denominating by time does not rescue it.** Arrivals per week are
immune to consolidation, which is the right instinct, but the baseline is not
there. vcs-cluster arrivals for the three weeks on record are 3, 10 and 40 - a
13x spread dominated by one capture burst. Variance/mean is 21.9 against the 1
a Poisson model assumes, so every interval computed that way is too narrow by
about 4.7x. Corrected, a two-week window has a 95% interval of roughly
[-15, 115] around an expected 50: a halving sits inside it and cannot be
called.

**What follows.** Do the consolidation and the root-cause round because they
are worth doing on their own merits - the cluster runs at r = 1.05, generating
more work than it closes, which is an argument from the baseline rather than
from a predicted result. Record the spawn counts as observation. Do not report
a rate change as evidence either way from a single round: with this dispersion
it would be noise dressed as a finding, which is the failure `PL-27S8` exists
to prevent, applied to the measurement rather than to a tightening.

**When a test does become available:** several more weeks of arrivals, or a
comparison between the treated cluster and the untreated ones over the same
window, which controls for the burst behaviour that ruins the time series. Not
now.
