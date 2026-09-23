---
id: PL-3W3P
title: A branch that edits a queue-only item's file for another item's reason claims that item: PL-0HPV's verify: reorder pass made docket flight report PL-LBW5, PL-RWBV, PL-YVV4 and PL-YZKK in flight on claude/kind-cerf-mizfzd, hiding them from docket next until #920 merges
priority: P3
effort: S
status: done
classes: defect
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md, .claude/skills/docket/modes/start.md, subprojects/docket/src/docket/checks.py
added: 2026-09-22
closed: 2026-09-22
payoff: a pass rewriting many item files no longer hides the queue-only items it passes through from docket next until it merges
verify: grep -q 'def test_a_queue_only_item_s_file_edited_under_another_id_is_not_claimed' subprojects/docket/tests/test_vcs.py
---

**Problem.** A branch that edits a queue-only item's file for another item's reason claims that item: PL-0HPV's verify: reorder pass made docket flight report PL-LBW5, PL-RWBV, PL-YVV4 and PL-YZKK in flight on claude/kind-cerf-mizfzd, hiding them from docket next until #920 merges

**Observed 2026-09-22, by the session that ran the pass.** Each of the four
declares `touches: docs/items` and nothing else, and none of this branch's
commit subjects names them; the reorder commit, led by `PL-0HPV`, rewrote their
`verify:` lines along with 92 others whose `touches` reach past the queue, and
only the four queue-only ones were marked. So the claim comes from
`vcs._queue_only_work`'s reading (`PL-7790`) - an edit to a queue-only item's
file is taken as that item's own work - rather than from a subject. It clears
itself once the branch merges; the cost is the window in between, and any
future pass over many item files will pay it again.

**Why it matters.** `docket next` withholds an in-flight item from every
session, so the four were unstartable for as long as `#920` stayed open, on a
claim nobody had made: the only session on that branch was working `PL-0HPV`.
Any later pass over many item files - a `verify:` sweep, a re-point, a rename -
would withhold every queue-only item it passed through the same way. It is
`PL-X3WZ`'s false mark, a queue edit read as a claim, readmitted by the
promotion built to recover `PL-X3WZ`'s residual.

**Reproduced 2026-09-22 against the pre-change `vcs.py`:**
`test_a_queue_only_item_s_file_edited_under_another_id_is_not_claimed` fails -
a queue-only commit led by `PL-0HPV` that writes `PL-K7QX`'s file, where the
base declares `PL-K7QX`'s `touches` inside the queue, reports `PL-K7QX` in
`branches`. And the existing `PL-7790` test was itself written in this shape
(subject led by `PL-XR8K`, file `PL-K7QX`'s), which is why it never caught it.

**Done when.** The `PL-7790` promotion reads only a queue-only commit that
leads with the item's own id and writes the item's own file - the shape the
`PL-VYSP` promotion already read - so a commit led by another id claims none of
the queue-only items whose files it passes through, and one led by the item's
own id still claims it. Pinned by
`test_a_queue_only_item_s_file_edited_under_another_id_is_not_claimed` and by
`test_an_item_whose_whole_deliverable_is_a_queue_edit_is_work_after_all`, whose
subject now leads with the item it writes.

**Generator check.** A re-entry: `PL-7790` (closed 2026-09-14) fed its
promotion from any edit to an item's file, which readmitted `PL-X3WZ`'s false
mark at a sibling site. Fixed with `PL-8FJK`, whose brief records the mechanism
the promotions share and carries it as a generator head.
