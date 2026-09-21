---
id: PL-YVP7
title: Question 2 of the gate staleness sweep cannot be recorded as decided: plan.py clears an entry by the milestone only when item.feature equals the milestone's feature, feature: is single-valued, and 147 of the 170 clearable Gate 2 entries already carry one - so re-labelling an entry interface-areas destroys the feature membership that bin/docket feature reports completion against
status: done
feature: gate-staleness-sweep
milestone: v0.5.1
added: 2026-09-21
closed: 2026-09-21
pr: 862
verify: bin/docket wave --no-git 2>/dev/null | grep -q 'cleared by the milestone itself:.*PL-CNCF'
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

## Decided (project owner, 2026-09-21, ratified)

**A second field, `cleared-by:`, read alongside the feature test** - chosen
over overwriting `feature: interface-areas` on each re-decided entry, which was
the instrument the 2026-09-21 gate decision named and which would have
destroyed the existing feature membership on 147 of the 170 clearable entries.

Ratified rather than specified: this was a session's recommendation the project
owner agreed with on one read ("Agree with recs"), so `CLAUDE.md` puts it back
to them on ordinary evidence - a measurement, a cost this case did not carry, a
constraint that appears later. It is not defended by "the owner decided it".

**`PL-WZVZ` is excluded by the same decision, ratified the same way** - chosen
over labelling it with the rest once the mechanism was safe. It is
`safety`-classed, inherited from Gate 1, carries `feature:
anesthesia-machine`, and `ROADMAP.md`'s gate section writes out by name where
it sits and why. The Question 2 mechanism answers yes for it; the entry is left
alone regardless.

## The case that was recommended: a second field, not a re-label

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

## Reopened on ordinary evidence, 2026-09-21: `plan.gate()` is the wrong function

**This reopens the ratified decision above under `CLAUDE.md`'s own terms** - a
constraint the case did not carry. The decision is sound about the *hazard*
and wrong about the *instrument*, and the error is this brief's, not the
owner's.

**What was verified, by running the commands rather than reading the code:**

- `bin/docket gate` prints `178 open debt items`. The frozen Gate 2 list holds
  183 entries. So `plan.gate()` does not read the frozen list at all - it
  partitions *every* open debt item in the store by `feature`.
- `bin/docket wave` prints `cleared by the milestone itself: PL-VN6M`, and that
  set is `roadmap.GateStatus.self_cleared`, computed from
  `own_scope = frozenset(milestone.own_scope_ids)` - **`ROADMAP.md`'s `Required
  scope` subsection**. It never reads `item.feature`.

So the sentence this brief quoted - `plan.py`'s rule is "Cleared by the
milestone itself: open debt carrying its feature" - describes a real function
that is **not** the one producing the number Question 2 is about. Wiring
`cleared-by:` into `plan.gate()`, which is what the ratified design says, would
move an entry in one command's display and move **nothing** in `clearable`, in
`self_cleared`, or in `is_clear` - which is what selects the CLEAR beat every
session is told to work.

**Why nobody caught it.** The one member, `PL-VN6M`, satisfies both routes: it
is named in Required-scope entry 9 *and* carries `feature: interface-areas`. A
single agreeing example hid the divergence. `ROADMAP.md`'s gate section had
already written the warning down - "the test is whether `Required scope` below
names the id, rather than whether the item carries the `interface-areas`
feature, and the two disagree on two entries" - and this brief read past it.

**What survives, unchanged.** The hazard is real and the count stands:
`feature:` is single-valued, 147 of the 170 clearable entries carry one, and
overwriting it destroys the membership `bin/docket feature` reports completion
against. Nothing here rehabilitates the re-label.

**Two further constraints the case did not carry**, both found by the
completeness critic and neither in the original design:

- `tools/doc_check.py`'s `check_gate_dispositions` is a **hard `make check`
  error** and computes an item's disposition from `ROADMAP.md` alone. A
  `cleared-by:` on an item file is invisible to it, so the field would fail
  `make check` for any entry not already on the frozen list.
- `self_cleared` operates on frozen-list *entries*, not items, and an entry may
  hold two ids for one problem. The existing rule requires **all** of an
  entry's open ids to qualify. A per-item field does not answer that question.

## Recommended instead: name the two ids in Required-scope entry 9

Entry 9 already commits v0.6.0 to relocating the exact mechanism `PL-CNCF` and
`PL-PGZF` turn on - `simulation_view.py`'s `plot_width_px=max(concentration,
wash_in)`, the column budget read across sibling plots. Naming them there is
therefore arguably not a scope widening at all but an honest statement of what
entry 9 already implies.

It needs **no code**: it uses the live instrument, it is what
`check_gate_dispositions` already reads, it leaves every `feature:` intact, and
it is auditable in the one document a reader consults.

**The cost, stated rather than smoothed over:** `Required scope` means the
milestone *builds* the entry, where the 2026-09-21 decision said "re-labelling,
not renegotiation". Whether naming a consequence of entry 9's own mechanism
inside entry 9 counts as renegotiation is the judgment, and it is the project
owner's rather than this brief's - which is why no edit has been made.

**Do not build `cleared-by:` on the strength of the ratification above.** It
was ratified against a mechanism description that this section falsifies.

## Resolved 2026-09-21: named in Required-scope entry 9, no field built

**Decided (project owner, 2026-09-21, ratified)** - chosen over building the
`cleared-by:` field, whose design the section above falsified before any code
was written, and over overwriting `feature:` on each re-decided entry.

`ROADMAP.md`'s Required-scope entry 9 now declares `PL-CNCF` and `PL-PGZF`
alongside `PL-VN6M` and `PL-9LNF`, with a paragraph recording why.

**Verified by running the chain, not by reading it.** Before:

    cleared by the milestone itself: PL-VN6M
    161 -> was 163 this gate can clear, 1 the milestone clears itself

After:

    cleared by the milestone itself: PL-VN6M, PL-CNCF, PL-PGZF
    Beat  clear the gate - 161 entries of 183 still open here, 3 the
          milestone clears itself

So the edit moves `self_cleared`, `clearable` and the beat line together -
which is precisely what wiring `cleared-by:` into `plan.gate()` would **not**
have done, and the reason the ratified field design was reopened.

**One mechanical detail worth carrying forward**, because it would have made
the edit a silent no-op: `_declared_ids` (`roadmap.py:613`) reads ids only from
a `(queue item ...)` slot, walking to the first token that is neither an id nor
a connective. An id added to entry 9's *prose* registers nowhere. The two ids
had to go inside the parenthetical.

**What this item does not do.** No new field, no change to `plan.gate()`, no
change to `tools/doc_check.py`. The divergence between `plan.gate()`'s
feature test and `GateStatus.self_cleared`'s Required-scope test is untouched
and still live - `ROADMAP.md`'s gate section already records that the two
"disagree on two entries". That is a real finding this item surfaced and did
not fix; it is filed separately rather than folded in here, because fixing it
is a change to the queue tool and this was a change to one document.
