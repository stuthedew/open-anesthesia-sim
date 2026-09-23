---
id: PL-8FJK
title: docket flight reads a branch whose commits touch only item files as capture or triage, so items a grooming branch is closing stay offerable: #914 drops PL-027, PL-043 and PL-ZBR6 and none reads as in flight
priority: P2
effort: S
status: done
classes: defect
feature: parallel-sessions
milestone: v0.5.6
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md, .claude/skills/docket/modes/start.md, subprojects/docket/src/docket/checks.py
added: 2026-09-22
closed: 2026-09-22
pr: 926
payoff: docket next stops offering an item a grooming branch is already dropping, so no second session starts work another has decided against
verify: grep -q 'def test_a_branch_closing_an_item_the_base_holds_open_is_in_flight' subprojects/docket/tests/test_vcs.py
root-cause-of: PL-3W3P, PL-7790, PL-8GV1, PL-VYSP
generator: spent - this record takes no later member: its mechanism, a claim read from where a commit wrote rather than what it did to the item, is recorded from 2026-09-23 on PL-MB2W, which ranks it live and holds the four instances filed since this closed
recurrences: 2026-09-22 PL-8GV1
---

**Problem.** `vcs._annotates_only` reads any commit whose whole diff sits in
the queue directory as capture or triage, never as work. A grooming branch is
exactly that, and it *closes* items. Observed 2026-09-22: #914
(`claude/oldest-items-relevance-a0awgl`, PL-Y4YG, which grooms the ten oldest
open items) drops PL-027 (confirm the slider write-back on a Flet client),
PL-043 (dial increments) and PL-ZBR6 (core raise-branch coverage), and
rewrites seven more. `bin/docket show` prints no in-flight mark for any of
them, and `docket flight` does not list the branch.

**Why it matters.** `docket next` offers an item that a branch is closing, so a
second session can start work that another has already decided to drop. That
is the "two sessions on one piece of work" error `_annotates_only`'s own
docstring calls the costlier of its two failure modes. PL-Q89J (`docket next
--oldest`, #913) makes the collision likely rather than rare. It hands out the
oldest items first, and those are the items a grooming pass targets.

**Direction, for triage.** The docstring records that PL-X3WZ's eight false
marks needed "nothing finer" than the path test. This is the counterexample.
Whether a queue-only commit changes an item's `status` to `done` or `dropped`
is decidable from the diff, and it separates closing an item from recording
one.

**Diagnosis, confirmed against the code 2026-09-22.** The session that
started this item handed off at the spend budget before writing any code,
so what follows is the whole of its work.

- `#914`'s branch did lead with the ids it closed: `2a616c70` "PL-Y4YG,
  PL-027, PL-ZBR6: groom the ten oldest open items against the tree" and
  `a07ff975` "PL-Y4YG, PL-043: drop PL-043, whose dial-increment premise is
  false". Both are queue-only and wrote each id's own file, so
  `_unmerged_commits` recorded all three in `_Walk.own_edits`. The only
  promotion that reads `own_edits` is the `needs-decision` one (`PL-VYSP`,
  `_deciding_on_base`). None of the three was at `needs-decision`, so each
  fell through to `FlightReport.editing`, which `docket next` does not read.
- `#919`'s empty-commit claim does not cover this case. The grooming
  session claims its own item (`PL-Y4YG`), not the items it disposes of.

**Recommended design, as handed off.** Add a third promotion in
`branches_in_flight`, after the `PL-VYSP` block and fed from the same `own`
map. For an id not already promoted, walk its carriers in rank order,
skipping any whose own-file edit `_superseded` found spent. Promote the
first carrier whose **tip** copy of the item is closed while the base holds
the item open:

- tip closed: `_items_at(ref)` for the path, then `_closed_at_ref`, both
  already used by `settled_branches`;
- base open: the id is in `_item_paths_on(base)` and not in
  `_closed_on_base`.

Read the tip rather than the commit, so that a branch which closed the item
and then reopened it is not marked. Feeding the promotion from `own` rather
than `edited` keeps the cost bounded by subject-led own-file edits. Fed from
`edited` it would cost a `git show` per mark, about 96 on `#920`'s branch
alone.

- `precedence`, the yield verdict `show` prints, reads `own_edits` for the
  `needs-decision` case (`_deciding_on_base`, `_modified_by`). Give it the
  same closure test, or `show` can mark a closing branch in flight and then
  leave it out of the verdict.
- One limit to state in the docstring: a closure whose subject does not lead
  with the closed id stays in `editing`. `CLAUDE.md` already requires a
  closing commit to lead with every id it closes.

**Sibling: `PL-3W3P`**, in which a branch editing a queue-only item's file
for another item's reason claims that item. It was captured on `#920`'s
branch `claude/kind-cerf-mizfzd` and landed on main with `#920`. It is
the mirror defect in the same block. The `PL-7790` promotion
(`_queue_only_work`) is fed from `edited`, meaning any edit, so `PL-0HPV`'s
`verify:` reorder claimed `PL-LBW5`, `PL-RWBV`, `PL-YVV4` and `PL-YZKK`
under a subject led by `PL-0HPV`. Feeding it from `own` instead (the subject
leads with the id and the commit wrote the id's own file) fixes that. All
three promotions then share one shape and differ only in the item-level
test: its deliverable is the queue (`PL-7790`), it is at `needs-decision`
(`PL-VYSP`), or this branch closes it while the base holds it open (this
item). Take `PL-3W3P` into the same change.

**Tests to add in `subprojects/docket/tests/test_vcs.py`:**

- the `#914` shape: a queue-only commit leading with X drops X while the
  base holds X open, and X is in `branches`;
- the same with X absent from the subject: X stays in `editing`;
- the base already closed after the squash: not in flight;
- closed and then reopened on the branch: not in flight;
- for `PL-3W3P`, a commit led by another id that edits a queue-only item's
  file does not claim it, and one led by the item's own id does.

**Docs to sweep:**

- the docstrings of `_annotates_only` and `branches_in_flight`;
- `subprojects/docket/README.md` at its `PL-VYSP` and `PL-7790` paragraphs;
- the "Two exceptions" paragraph in `.claude/skills/docket/modes/start.md`,
  which becomes three.

**As built, 2026-09-22.** The design above, with three departures, each for a
reason the handoff could not see:

- **The three promotions share one helper, `vcs._own_edit_claims`,** fed from
  the subject-led own-file map and narrowed by the same `_superseded` test,
  rather than a third block beside two. That is what makes `PL-3W3P`'s fix and
  this one a single change, and it is what `precedence` now calls.
- **`precedence` reads all three, not only the closure,** and applies the
  supersession test too. `show` prints the in-flight mark *through* the
  verdict, so a promotion read by `branches_in_flight` and not by `precedence`
  printed no mark at all - true of every `PL-7790` promotion before this. A
  landed design round's ref was likewise still a carrier in the verdict while
  the mark had dropped it.
- **The tip is read at the paths the round wrote,** through `_closed_at_ref`,
  rather than through `_items_at(ref)`. That costs one batched `git show` per
  carrier where `_items_at` costs an `ls-tree -r` of about 1,500 entries per
  ref, on the hot path of `next`, `list` and the digest. What it gives up is a
  later rename of the file by a commit leading with some other id, which then
  reads as "open" and leaves the item offered.

`_modified_by` is not applied to the closure: a capture files its item open, so
the tip test already excludes it, and `git log --name-only` lists only a
rename's destination, so the parent test would refuse a closure that also
retitled its file (`PL-J16N` has that gap in the `PL-VYSP` promotion).
Checked against real git on a throwaway branch dropping `PL-024` in one
queue-only commit led by its id: `branches_in_flight` and `precedence` both
name the branch. `bin/docket flight` on this clone's fifteen remote branches
reads identically before and after, in 0.64 s against 0.68 s.

**Reproduced 2026-09-22 against the pre-change `vcs.py`:**
`test_a_branch_closing_an_item_the_base_holds_open_is_in_flight` fails - the
closing branch is absent from `branches` - and so do
`test_precedence_names_the_carrier_every_own_edit_promotion_marks` and
`test_precedence_does_not_make_a_carrier_of_a_round_the_base_already_holds`.
Reading the closing commit's copy instead of the tip fails
`test_a_branch_that_closed_an_item_and_reopened_it_claims_nothing`.

**Done when.** A queue-only commit that leads with an item's id and writes its
own file claims the item where the branch's tip holds it closed and the base
holds it open, and not where the base already records it closed, where the tip
has reopened it, or where the subject leads with another id. `docket show`
prints the claim through `precedence`, which reads the same helper.

**Generator check.** One mechanism with `PL-7790`, `PL-VYSP`, `PL-3W3P` and
`PL-8GV1`, and no head named it, so this item carries it: `_annotates_only`
reads where a commit wrote and never what it did to the item, so each shape of
queue-only work a pass does without claiming the item has been recovered by its
own promotion, one incident at a time, each fed its own way. This change gives
the three one feed and one helper, which retires the divergence half
(`PL-3W3P`, and `precedence` missing two of the three). It does not retire the
per-shape half: `PL-8GV1`, a pass blocking an item it never claimed, was filed
the same day, so the verdict is `live`.
