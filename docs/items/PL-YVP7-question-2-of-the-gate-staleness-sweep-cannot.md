---
id: PL-YVP7
title: Question 2 of the gate staleness sweep cannot be recorded as decided: plan.py clears an entry by the milestone only when item.feature equals the milestone's feature, feature: is single-valued, and 147 of the 170 clearable Gate 2 entries already carry one - so re-labelling an entry interface-areas destroys the feature membership that bin/docket feature reports completion against
status: untriaged
feature: gate-staleness-sweep
added: 2026-09-21
---

**Problem.** Question 2 of the gate staleness sweep cannot be recorded as decided: plan.py clears an entry by the milestone only when item.feature equals the milestone's feature, feature: is single-valued, and 147 of the 170 clearable Gate 2 entries already carry one - so re-labelling an entry interface-areas destroys the feature membership that bin/docket feature reports completion against

## The mechanism, read against the code rather than the decision

`subprojects/docket/src/docket/plan.py`'s `gate()` is four lines and admits no
second route:

```
inside = [i for i in debt if feature and i.feature == feature]
outside = [i for i in debt if not (feature and i.feature == feature)]
```

`Item.feature` is one string. So "the entry carries `feature: interface-areas`"
is not a label added beside what an entry already has - it is a label written
*over* it.

**The counts, measured 2026-09-21 across the 170 clearable Gate 2 entries.**
147 carry a `feature:` and 23 do not. Every Question 2 candidate the sweep has
confirmed so far is in the 147: `PL-CNCF` and `PL-PGZF` both carry
`chart-readout`, and `PL-WZVZ` carries `anesthesia-machine`. So the collision is
not an edge case in this bucket; it is the bucket.

**What is lost is not cosmetic.** `CLAUDE.md` makes `feature:` the instrument a
reader uses to ask whether a problem is finished - "lead with the problem and
name the `feature:` its items carry, so 'is that dealt with?' has a command
behind it". Overwriting `chart-readout` on two of its members makes
`bin/docket feature chart-readout` report a completion that is not true, and
there is no way to ask the original question afterwards.

**`PL-WZVZ` is the sharpest case and should not be re-labelled either way
without a decision.** It is Gate 1's inherited entry, `safety`-classed, and
`ROADMAP.md` § "Debt gate: the frozen list" writes out by name where it sits
and why. Its blockers `PL-TH35` and `PL-R1WQ` are both v0.6.0 Required scope,
which is what makes Question 2 answer yes for it - and acting on that answer
would both contradict recorded prose and destroy its `anesthesia-machine`
membership.

**Decision needed.** Whether Question 2's verdict is recorded by overwriting
`feature:` (the ratified wording, which destroys existing feature membership on
147 of 170 entries) or by a second field read alongside it. Until this is
answered, no Gate 2 entry is re-labelled: the sweep records its Question 2
verdicts and stops short of writing them.

## Recommended: a second field, not a re-label

Record the claim where it can be read without displacing anything:
`cleared-by: v0.6.0` on the entry, and `gate()` puts an item `inside` when it
carries the milestone's feature **or** names the milestone in `cleared-by:`.

Three reasons this is the better route rather than merely the gentler one:

1. **It is auditable.** A re-label says an entry is in the bucket; it never
   says why. A named field holds the claim, and a reviewer can ask whether it
   is true. The safety-critical standard's preference for traceability over
   convenience is the same preference here.
2. **The project has already noticed the proxy misfires.** `ROADMAP.md`'s own
   gate section records that "the test is whether `Required scope` below names
   the id, rather than whether the item carries the `interface-areas` feature,
   and the two disagree on two entries." That disagreement is this defect seen
   from the other side.
3. **It is reversible.** If Question 2 is answered wrongly for an entry, a
   field is removed. An overwritten `feature:` is only recoverable from git
   history by someone who knows to look.

**What this does not touch.** Question 1 - the staleness half - is unaffected
and is being completed in the same pass. Nothing here reopens the ratified
*intent*, which is that an entry v0.6.0 would re-decide is cleared by the
milestone rather than before it. Only the recording instrument is in question.
