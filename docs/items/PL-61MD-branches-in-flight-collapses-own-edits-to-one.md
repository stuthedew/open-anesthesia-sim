---
id: PL-61MD
title: branches_in_flight collapses own_edits to one ref per id before the superseded and needs-decision tests, so a bystander's landed design-round commit drops a live round on the same item
priority: P2
effort: S
status: done
classes: defect
feature: carrier-collapse
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, ROADMAP.md
added: 2026-09-19
closed: 2026-09-19
verify: grep -q 'def test_a_landed_design_round_on_a_bystander_branch_does_not_drop_a_live_one' subprojects/docket/tests/test_vcs.py
---

**Problem.** branches_in_flight collapses own_edits to one ref per id before the superseded and needs-decision tests, so a bystander's landed design-round commit drops a live round on the same item

**The third instance of `PL-2BZY`'s mechanism, and the one nearest the case it
was found in.** `PL-VYSP` promotes a queue-only commit to a claim where it led
with an id, wrote that id's own file, and the base records the item at
`needs-decision` - which is what a design round looks like. That promotion
reads `_Walk.own_edits`, and `branches_in_flight` collapses it to one ref per
id before either of its two per-ref tests runs.

**Mechanism.** `own_edits` is keyed `(ref, id)`, so the walk itself keeps every
carrier; the collapse is in the caller:

```python
held_own = own.get(identifier)
if held_own is not None and rank.get(held_own[0], len(rank)) <= rank.get(name, len(rank)):
    continue
own[identifier] = (name, commit, paths)
```

`deciding` then drops an id whose every path `_superseded` finds the base
holds, and `_modified_by` drops one whose commit did not actually change the
file. Both are facts about the chosen ref. So a bystander branch whose
design-round commit has landed - byte-identical to the base - suppresses a live
round another ref is running on the same item, and `bin/docket show` calls it
startable.

**Why it matters.** This is the reading `PL-VYSP` built to stop `bin/docket
show PL-BHVM` calling a held item startable, on exactly the items a recorded
generator ranks above every band but `P0`. A design round leaves no diff
outside the queue, so nothing else marks it.

**Done when.** `own` keeps every carrier per id in candidate order,
`_superseded`, `_deciding_on_base` and `_modified_by` judge each, and the first
survivor is reported; the id leaves the promotion only where every carrier
fails. A test pins both directions.

**What it came to: two of the three tests are per carrier, not three.**
`_superseded` reads one ref's copy of a path and `_modified_by` reads one
commit's own parent, so both are facts about a carrier and both are asked of
each. `_deciding_on_base` is not: it reads the item's status off the *base*,
which is one tree and one answer per id however many refs carry it. So it is
asked once per id, between the two - which is also what keeps the promotion at
one `git show` per id rather than one per carrier, and is why the brief's "judge
each" overstates it by one test.
