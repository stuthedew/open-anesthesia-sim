---
id: PL-WNQT
title: bin/docket stranded reports a one-path commit as work left behind whenever a later merge edits that file, and its recovery recipe would revert the newer work
priority: P2
effort: M
status: ready
classes: defect
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, tests/unit/test_docket_branch_guard.py
added: 2026-09-14
verify: grep -q 'def test_a_later_merge_touching_the_file_is_not_work_left_behind' tests/unit/test_docket_branch_guard.py && uv run pytest tests/unit/test_docket_branch_guard.py
recurrences: 2026-09-25 PL-TFF9 withdrawn 2026-09-25 PL-TFF9
---

**Problem.** bin/docket stranded reports a one-path commit as work left behind whenever a later merge edits that file, and its recovery recipe would revert the newer work

**Found 2026-09-14**, reproduced twice against a freshly fetched `main` at
`5c65f30`. `bin/docket stranded`'s second half reports:

```
origin/claude/lucid-darwin-o0eg7u  (12 files of its work already landed)
  f35bdc8f4  PL-TFX5: `drawn_window`'s docstring points at a method that does not exist
    src/anesthesia_sim/app/controller.py
  recover: git checkout origin/claude/lucid-darwin-o0eg7u -- src/anesthesia_sim/app/controller.py
```

That commit's whole content is one line, and **it is on `main`**:
`src/anesthesia_sim/app/controller.py:1114` reads ``for those instants is
refused, and rightly - see `evaluate_anchored`.`` - the corrected spelling, with
no occurrence of `evaluate_window` left anywhere in the file. It landed in
`#570`'s squash. Nothing is stranded.

**Why the safeguard cannot fire here.** `_orphaned`'s rule is that a commit
whose changes are *partly* on the base is a commit the merge took - counted in
paths, so that a squash merged against a moving base still reads as a merge.
A commit with **one** path has no second path to vote with: `#572` then edited
`controller.py`, the branch's copy of that file no longer matches the base's,
the single path reads as never landed, and the whole commit with it. So the
false positive is not about this commit's content at all; it fires for any
one-path commit whose file a later merge touches.

**Why it matters more than an extra line of output.** The printed recipe is a
whole-file checkout from a branch whose copy predates `#572`, so a session
following it reverts every change `#572` made to `controller.py` - simulator
code, on the specialist standard's side of the tree. This is `PL-XLQ5`'s harm
shape (a `git checkout` overwriting the merged copy with an older one) reached
through the *branch* half rather than the item half, and the reader has nothing
in the output that would make them doubt it: the branch is named, the commit is
named, and 12 of 13 files are correctly reported as landed.

**Done when.** A one-path commit whose file the base has since changed is not
reported as work left behind, or - where that cannot be decided - the recipe is
not a whole-file checkout of a file the base has moved under. A test pins the
shape: a branch whose single-path commit landed in a squash, with a later
commit on the base editing the same file.

**What is not the answer.** Comparing the commit's own hunk against the base
is a content comparison of the kind `_orphaned`'s docstring already refuses -
"no content comparison of the outstanding three can see that". The unit is the
question: the rule counts paths because a squash takes whole commits, and a
one-path commit is where counting has nothing to count.

**Why it matters.** This is the other half of `bin/docket stranded`'s output
from `PL-MBTZ` - the "work its own pull request left behind" walk rather than
the item-recovery walk - and it fails the same way, by prescribing a fix that
destroys the newer state. A one-path commit is read as left behind whenever any
later merge edits that path, which is the common case on a file more than one
session touches, and the recipe then reverts the later work. Both halves of one
command therefore produce confidently wrong, destructive advice under conditions
that are normal rather than exotic, and the skill's own text tells a session to
follow it. That is `CLAUDE.md`'s "gives a wrong answer silently" test, and it is
the reason these two are worth doing together rather than in queue order.

**Done when.** The left-behind walk distinguishes a commit whose content the
base has since superseded from one the base never took, so a path edited by a
later merge is not reported as left behind, and the recovery it prints cannot
revert newer work. `tests/unit/` covers a path a later merge edited.

**Re-pointed by `PL-BHVM`'s design round, 2026-09-19.** Question 2 — did the
ref's work land. The ordering is settled and needs no further decision: the
exact ref test answers where `refs/pull/<n>/head` resolves, `vcs.orphaned`
answers everywhere else, and because that ref is deletable on request the exact
test is **not a superset** of the portable one even in principle — so `orphaned`
is never retired. Where the two disagree, the exact test wins and the
disagreement is printed rather than resolved silently, which answers the
question `PL-R808` leaves open.
