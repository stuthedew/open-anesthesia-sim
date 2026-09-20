---
id: PL-2DTK
title: docket verify --self cancels an added line against its removal only within the commits it selects per id, so an item is charged with removing an assertion a commit that does not name it had added on the same branch
priority: P2
effort: M
status: blocked
classes: defect
feature: verify-false-reject
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
blocked-by: PL-4W2L
added: 2026-09-19
verify: grep -q 'def test_a_removal_is_not_charged_to_an_id_whose_selection_excludes_the_addition' subprojects/docket/tests/test_verify.py
---

**Problem.** docket verify --self cancels an added line against its removal only within the commits it selects per id, so an item is charged with removing an assertion a commit that does not name it had added on the same branch

**Found 2026-09-19, twice in one session, on the branch closing `PL-HWW1`.**

**The mechanism.** `PL-VP40` made the assertion check cancel an added line
against an identical removed line *within the same file*, so a line a branch
adds in one commit and removes in the next is not reported. That fold runs
over `_diff_text`, which concatenates **the commits selected for this id** -
by subject, or by the commit touching the item's own file. The cancellation is
therefore scoped to the selection rather than to the branch, and where the
addition sits in a commit that selection excludes, the removal is charged to
an item that did not make it.

**The two instances.** Both are the same two lines - a test fixture id
corrected from `PL-STUV` to `PL-RSTW`, because `U` is outside `ID_ALPHABET`
(that is `PL-R77L`):

- `PL-4PC5`: the adding commit's subject named `PL-HWW1` and `PL-6P9Y` only.
  Repairable, and repaired, because that commit genuinely carried `PL-4PC5`'s
  work - it contained the test `PL-4PC5`'s own `verify:` greps for - so
  naming it in the subject made the record *more* accurate, not less.
- `PL-C4RS`: **not repairable the same way.** `PL-C4RS` is a `ROADMAP.md`
  prose reconciliation with nothing to do with `test_roadmap.py`, so adding
  its id to the test commit's subject would be false. Its diff is selected
  because a later commit edits its item file; the adding commit neither names
  it nor touches that file. It closed on a `REJECT` for a removal made by
  another commit, with `make check` green and its own `verify:` passing.

**Why it matters.** The guard is the close-out's own proof, and `CLAUDE.md`'s
`docket` skill says to re-run until it says `ACCEPT`. An unclearable `REJECT`
on correct work trains a reader to skim the block where a real protected-path
or suppression failure is printed - which is exactly the harm `PL-69JZ` and
`PL-7XTS` recorded for the four commission checks, arriving through a
different door. `falsifies:` is not the answer: nothing was falsified, and a
session may not declare one for itself mid-work anyway.

**Where.** `subprojects/docket/src/docket/verify.py` - the fold in
`_diff_text`'s counters and the per-id commit selection that feeds it. The
shape of a fix is that cancellation should see the *branch's* additions rather
than the selection's, while the reported removals stay per id; whether that is
a second diff pass or a branch-wide addition set is the design question.

**Not confused with `PL-R77L`**, which is the fixture id itself, or with
`PL-CWD4`, which is a `verify:` command that can never pass. This is the
audit's own arithmetic.

**Done when.** A branch where one commit adds an assertion and a later commit
removes it reaches `ACCEPT` for every id the branch names, whichever commit's
subject names which id - and a test in `subprojects/docket/tests/test_verify.py`
drives `PL-C4RS`'s shape specifically: the addition in a commit the id's selection
excludes, the removal in one it includes, asserting the removal is not charged.
What the audit *reports* stays per id; only what the cancellation can see widens
to the branch.
