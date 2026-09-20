---
id: PL-7K8Y
title: docket record normalises front-matter key order as it writes pr:, so docket verify reads that item's backfill as a content edit rather than a sanctioned pr write
priority: P2
effort: S
status: done
classes: defect
feature: delegation
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/store.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests
added: 2026-09-16
closed: 2026-09-20
payoff: a close-out that followed the instructions stops coming back REJECT, so no session has to rebuild its branch history to clear a line the tool itself wrote
verify: grep -q 'def test_record_on_non_canonical_key_order_classifies_as_pr' subprojects/docket/tests/test_verify.py
---

**Problem.** `bin/docket record` writes `pr: N` into a closed item's front
matter and, on an item whose keys are not already in canonical order, also
reorders them. On `PL-NW76` it moved `verify:` from above `touches:` down past
`closed:`. `subprojects/docket/src/docket/verify.py:sanctioned_queue_edit`
classifies a queue edit as a `pr` backfill only when the diff has **no removed
lines** (`if removed: return ""`), and a reorder is a removal plus an addition.
So that one item's backfill was counted as a path outside the current item's
`touches`, and `bin/docket verify` reported `FAIL diff stayed inside touches`
for a close-out that had followed the skill's instruction exactly.

**Why it matters.** This is `PL-ZYQC`'s shape returning through a door the fix
did not cover. The `docket` skill's close-out says to run `record` bare and
"let the write ride a commit you are already making"; `sanctioned_queue_edit`
exists precisely so that following it does not produce a `REJECT`. It does for
any item whose key order differs from canonical, and the failure names the item
file rather than the cause, so the reader sees an out-of-commission edit and has
to go and diff it to learn that a tool wrote it.

The cost is not only the confusion. `sanctioned_queue_edit` reads the
**per-commit** diffs (`git show --format= <commits>`), not the net tree, so
correcting the order in a later commit on the same branch does not clear it -
the branch then carries both the removal and its undo. The only remedies are to
rebuild the branch history or to leave the FAIL standing.

**Found 2026-09-16** while closing `PL-R0Q0`, which cost a branch rebuild. The
same seven backfills landed independently in `#627` (`PL-NLP4`), which kept the
normalised order - so the two branches then conflicted on `PL-NW76` alone.

**Where.** `subprojects/docket/src/docket/verify.py` `sanctioned_queue_edit`;
whichever writer in `subprojects/docket/src/docket/` serialises an item's front
matter for `record`; `subprojects/docket/tests/`.

**Shape, not a decision.** Either `record` leaves key order alone when it is only
adding `pr:`, or `sanctioned_queue_edit` compares parsed front matter rather than
raw diff lines so that a pure reorder plus a `pr:` addition still classifies as
`pr`. The first is narrower and keeps the classifier's "no removals" rule exact,
which is what makes the exemption safe; the second is more robust but widens what
a sanctioned edit may contain. Worth checking first whether any item's key order
is non-canonical today, since that decides how often this can fire.

**Done when.** Running `bin/docket record` on an item whose front-matter keys are
in a non-canonical order produces a diff that `sanctioned_queue_edit` classifies
as `pr`, and a test in `subprojects/docket/tests/` pins it against exactly that
item shape.

**Measured 2026-09-19, as `PL-L4YG` landed `docket set`.** 96 of 1,189 item
files carry a key order `render_item` would not write, so `record` reorders
any of those it reaches. `docket set` writes canonical order at triage, which
shrinks that population from here on and leaves the existing 96 as they are.
