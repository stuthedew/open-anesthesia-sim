---
id: PL-NPWP
title: bin/docket stranded's ahead list keys on textual difference between the base's copy and a branch's, so a branch holding a stale copy is reported forever and no amount of recovery can empty the list - which is the completion test PL-DZM1 was written against
priority: P2
effort: M
status: done
classes: defect
feature: stranded-report-fidelity
milestone: v0.5.23
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-09-21
closed: 2026-10-11
pr: 1402
payoff: stranded's list can reach empty again, so a row in it means somebody has work to recover rather than that a fork is old
verify: grep -q 'def test_a_copy_a_squash_took_and_the_base_reworded_is_not_reported' subprojects/docket/tests/test_vcs.py
---

**Problem.** bin/docket stranded's ahead list keys on textual difference between the base's copy and a branch's, so a branch holding a stale copy is reported forever and no amount of recovery can empty the list - which is the completion test PL-DZM1 was written against

**Measured 2026-09-21.** `bin/docket stranded` reported 7 items the default
branch holds and a branch edits, across 5 distinct refs. Three of those refs -
carrying 5 of the 7 items - are not on the remote at all: it holds 7 heads, and
those three survive only as this checkout's own remote-tracking pointers, which
`fetch_remote` refuses to prune on purpose (`PL-HKF4`). Diffing three of the
reported copies against the base's shows the branch copy is the *shorter* one in
every case, by 14, 48 and 75 lines: the base has grown past a fork, which is not
an edit the base is missing.

**Why it matters.** This is the second compounding-friction test in `CLAUDE.md`
- an advisory being routed around. The list cannot reach empty by any action a
reader can take, because a copy forked before the base moved differs textually
forever, so every run prints rows that mean nothing and the reader learns to
skim a report whose whole purpose is to be read when it is rare. `PL-DZM1` was
written against emptying this list as its completion test, which no amount of
recovery can satisfy. The direction of the error is the quiet one: a real
stranded edit arrives in a list already full of false ones.

[superseded 2026-10-11: met for an untouched copy by `#1160`; the rest is below]
**Done when.** A branch copy that differs from the base's only because the base
moved on is not reported as ahead, so a checkout with nothing genuinely stranded
prints an empty list; and a test in `subprojects/docket/tests/test_vcs.py` drives
a base that has advanced past an untouched branch copy.

**Re-pointed at `tools/left_behind_check.py`, 2026-10-11 (`PL-2C53`): that
check answers none of this.** It reads branch tips against the heads merged pull
requests froze, and opens no item copy, so the ahead list is outside it.

**The untouched copy the brief names was fixed by `PL-WVSX` in `#1160`.**
`stranded` now reads each ref's change since its fork through `vcs._Landings`
before it opens a copy. A copy the ref never wrote since its fork is the fork's
own, and is skipped unopened however far the base has moved. One in the landed
half is a copy the base itself wrote since the fork.
`test_a_copy_the_base_has_held_and_moved_past_is_not_reported` drives a base
that rewrote an untouched branch copy, and
`test_a_branch_copy_the_base_has_only_added_to_is_not_reported` one that only
grew. Reproduced on real git 2026-10-11: a branch that forked with an item and
never touched it is not reported after the base moved the item from `untriaged`
to `ready`, reworded its prose and appended a paragraph. `_standing` alone reads
that copy as ahead, since it holds the old line. A control branch that added a
paragraph is reported. On this checkout the list holds one row, `PL-W3Q5`, a
live edit with `#1393` open on it.

**What is still this item's: a copy the branch wrote, which a squash merged with
another edit and the base then reworded.** Reproduced on real git 2026-10-11. A
branch appends a paragraph to an item. The base, through another pull request,
moves the item's `status:`. The branch squash-merges, and the base rewords the
branch's paragraph. `stranded` then reports the branch's copy as an edit the
base lacks, for as long as the ref stands. Yet `vcs.change_landed` on the
branch's commit names the squash, `PL-K7QX: a finding (#2)`, as where it landed.
The squash wrote a merged blob, so the branch's own blob is outstanding in
`_Landings`' split, and `_standing` then finds the reworded line missing from
the base. `change_landed` is the change-level test that `orphaned` and the exact
check already read (`PL-GHHW`). `stranded`'s item half is the reader of that fact
left off it. The ref has to outlive its squash merge, which GitHub's deletion of
a merged head branch makes rare. A push after the merge recreates one, though,
and while the item is open on the base `tools/branch_sweep.py` keeps such a
branch for the edit.

**Done when.** A branch copy of an item whose every change since the fork the
base has taken, by `vcs.change_landed` rather than a new comparison, is not
reported as ahead, so the list holds only copies carrying something the base
never took. A test in `subprojects/docket/tests/test_vcs.py` drives a squash that
merged the branch's edit with another one and a base that reworded it afterwards,
and the two fork tests above still pass.

**Done 2026-10-11 (`#1402`).** Re-confirmed first, on real git at `1422c404`:
the brief's shape reproduced as written, and so did the same shape without the
rewording, since a `status:` the base moved to `ready` is not a closure and
`_standing` calls the branch's copy ahead on that field alone. `stranded` now
asks `vcs.change_landed` of every commit a ref wrote the item in, for a copy
the text calls ahead and only where the split was read, and a copy whose every
commit the base took is not reported (`vcs._ItemChanges`).
`test_a_copy_a_squash_took_and_the_base_reworded_is_not_reported` drives the
shape, with a commit pushed after the merge still reported beside it, and the
two fork tests pass unchanged.

The commits are the ref's non-merge commits the base does not hold that wrote a
file of the item under either name a retitle gave it (`vcs._item_edits`).
Asked of the newest commit, or of the item's current name alone, a retitle the
base cherry-picked would have cleared a note written under the old name that
nothing took: `test_a_retitle_the_base_took_leaves_a_note_written_under_the_old_name_reported`.
A listing git did not answer, and a git older than 2.40, keep the copy and mark
the read partial (`test_a_change_git_would_not_place_leaves_the_copy_reported`).
A mutation of each guard fails one of the three tests.

Measured on 2026-10-11, against refs fetched into a scratch clone: on 299 merged
pull-request heads (`#1100`-`#1401`) and on the commit before the base merge 192
of them end with, no copy reached the new test, before or after. Each of 151 of
those heads given one commit pushed after its merge was reported before and
after, and the read went from 8.7 s to 19.0 s, about 70 ms a reported copy. On
this checkout `PL-3800`'s live edit (`#1397`) is still the one row.

What it still reports, and why nothing was filed: a branch that wrote an item in
two commits whose lines sit next to each other, a closure and then the `pr:`
recorded under its `closed:`, leaves a squash holding both, and the first
commit replayed alone conflicts with it. That is `change_landed`'s documented
recall cost, it errs toward reporting, as every row did before this, and no
population above produced one. `_ItemChanges` names it where a reader of such a
row would look. The docket README's paragraph on how a direction is decided
still described the rule `PL-WVSX` replaced, and now describes both changes.
