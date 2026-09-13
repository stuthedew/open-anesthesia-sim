---
id: PL-CSHL
title: Pre-registered test: close the 15 open vcs.py items as one root-cause round and count what they spawn against the cluster's own baseline of 1.05
priority: P3
effort: S
status: done
classes: infra
feature: parallel-sessions
touches: docs/items
added: 2026-09-12
closed: 2026-09-13
pr: 504
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
Six of the eleven `ready` items are entries on v0.5.0's frozen debt gate, so
they are owed before the milestone begins whatever happens to `r`. (Corrected
2026-09-13 while running it: the un-withdrawal said ten, and `bin/docket wave`
names six - `PL-JSRH`, `PL-PMT7`, `PL-R6D8`, `PL-W1LN`, `PL-XLQ5`, `PL-YDL6`.
The other five are `defect`-classed and so are debt by the gate rule; they were
captured after the freeze, so they fall to the next gate rather than this one.) The
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


---

## The result, 2026-09-13

RESULT: N=9 closed, 3 spawned. H0 at N=9 expects 9.5 and rejects at 5%
one-sided on 4 or fewer, so **H0 is rejected**: the batch spawned a third of what
the cluster's own baseline of 1.05 predicted. Spawn rate r = 3/9 = 0.33, against
r_vcs = 1.05 and a whole-lane r = 0.69.

**The nine closed.** `PL-6BDX`, `PL-8MJ3`, `PL-JBRC`, `PL-JSRH`, `PL-PMT7`,
`PL-R6D8`, `PL-XLQ5`, `PL-Y31G`, `PL-YDL6`.

**The three spawned**, each attributed by the pre-registered rule - the creating
commit's subject leads with `PL-YDL6, PL-8MJ3` - and counted from git history
rather than from memory: `PL-QNYF` (a `docket check` error now reachable with no
remedy named), `PL-3LLZ` (four test fakes each taught the same git question),
`PL-7XNX` (one subprocess per edited item where one per ref would do).

**Two of the eleven did not close**, which is why N is 9 rather than 11 and why
the test ran at its lowest useful power:

- `PL-W1LN` moved to `needs-decision`. Its own **Done when.** allowed only "the
  guard covers it" or "the topology cannot be produced here", and the
  reproduction ruled out the second: seven commands produce the uncaught walk,
  which reports three of `main`'s commits as in-flight work with every emitted
  commit carrying a parent. Covering it soundly needs a trade the owner should
  pick, so the item carries the recipe and the three options.
- `PL-GVC0` left `ready`. Making the id prefix configurable means four regexes
  compiled at import from `store.ID_PATTERN` become per-config, threaded through
  `store`, `vcs`, `config` and every reader of `BRANCH_ID_RE`, `ITEM_FILE_RE`,
  `LEADING_IDS_RE` and `ANY_ID_RE`. Its own brief argues for doing it when a
  second consumer appears and not before, and having read the code that is the
  right call: the seam's only validation would be a synthetic second prefix.

**What the low count is and is not evidence for.** It is not evidence that
`PL-BHVM`'s root-cause account holds, because that account was already refuted -
twenty of twenty ref-lifecycle items came back `unaffected` and no `blocked-by`
edge was proposed. What the batch actually found is weaker and real: five of the
nine turned on one question - what evidence proves a ref's work is on the base -
and two rules answered them. `_annotates_only`, already in the module, decided
three of them (`PL-JBRC`, `PL-YDL6`, and the `record`-write half of `PL-8MJ3`'s
reasoning); `_superseded`, written once for `PL-XLQ5`, then answered `PL-8MJ3`
unchanged. So the mechanism is reuse of a decided rule rather than consolidation
of items.

**The threat to the inference, stated plainly.** One session closing nine items
has fewer opportunities to file than nine sessions closing one each, for reasons
that have nothing to do with root causes: findings that would each have ended a
session and been captured on the way out were instead fixed in place or folded
into a sibling item's brief, and a session already holding the whole module
recognises a finding as the same finding. That is a batching effect, not a
root-cause effect, and this design cannot separate the two - both predict a low
count. A cleaner test would close nine unrelated items in one session and compare,
which is worth one item rather than a redesign of this one.

The count was also made against the session's own interest, and that is worth
recording: a pre-registered spawn count rewards not filing, so the three above
were filed on the capture rule and counted rather than held. Any future run of
this test should expect that pressure and say how it handled it.
