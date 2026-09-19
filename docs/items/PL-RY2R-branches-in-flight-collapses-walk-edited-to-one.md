---
id: PL-RY2R
title: branches_in_flight collapses walk.edited to one ref per id before the superseded test, so a stale file edit on a bystander branch takes a live edit's mark with it
priority: P2
effort: S
status: done
classes: defect
feature: carrier-collapse
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, ROADMAP.md
added: 2026-09-19
closed: 2026-09-19
verify: grep -q 'def test_a_superseded_file_edit_on_a_bystander_branch_does_not_drop_a_live_one' subprojects/docket/tests/test_vcs.py
---

**Problem.** branches_in_flight collapses walk.edited to one ref per id before the superseded test, so a stale file edit on a bystander branch takes a live edit's mark with it

**The same mechanism as `PL-2BZY`, one reading over.** That item fixed
`_Walk.ids`, which `_taken_on_base` judges per ref; `_Walk.edited` has the
identical shape and feeds `_superseded`, which is also a per-ref test.

**Mechanism.** `_unmerged_commits` keeps one `(ref, path)` per id in `edited`,
chosen by `nearer` - candidate rank - as the walk runs. `branches_in_flight`
then drops any mark whose path `_superseded` finds the base already holds:

```python
edited = {
    identifier: name for identifier, name, path in marks if path not in superseded_by_ref[name]
}
```

So where two refs have both edited one item's file and the rank-first ref's
copy has landed - a squash merge, a rebase, a cherry-pick - the id leaves
`FlightReport.editing` entirely, though the second ref's edit is unmerged and
is exactly the collision the mark exists to name. The `walk.unbounded` filter
above it has the same shape: an id whose rank-first editor is a ref the walk
could not read loses the mark even where a readable ref also edited the file.

**Why it matters.** `editing` is the weaker mark `PL-N1JK` added for the case
the in-flight mark cannot reach: two triage passes on one item, whose diffs
never leave `docs/items/`, colliding at merge with one answer discarded.
Losing it is silent - `flight` and `triage` print the marks that survived, and
nothing says one was collapsed away.

**Done when.** `_Walk.edited` carries every `(ref, path)` per id in candidate
order, `branches_in_flight` reports the first whose path `_superseded` did not
take, and the id leaves `editing` only where every carrier's edit is
superseded or unread. A test pins the pair the way
`test_a_spent_claim_on_a_bystander_branch_does_not_drop_a_live_one` does for
`PL-2BZY`.

**One entry per ref, and that part of the collapse stays.** `nearer` decided two
things at once: which ref to keep for an id, and which path to keep for a ref
when one commit changed two - a round that renames the item's file. Only the
first was wrong. The replacement appends the first path each ref offers, which
is the newest commit's in walk order, so the within-ref choice is unchanged and
`nearer` itself is now dead and removed.
