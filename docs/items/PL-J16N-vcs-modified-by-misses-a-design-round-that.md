---
id: PL-J16N
title: vcs._modified_by misses a design round that renames its item's file: git log --name-only reports only a rename's destination, which the commit's parent never held, so PL-VYSP's promotion reads the round as a capture - and the test fake lists both paths, so test_a_round_that_renames_the_item_file_still_claims_it passes against a git that does not behave that way
priority: P3
effort: S
status: ready
classes: defect
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the first 2026-09-23 triage pass
added: 2026-09-22
payoff: a design round that retitles its needs-decision item in its last commit stays withheld from docket next, and the rename test stops passing against a git that does not exist
verify: grep -q 'def test_flight_claims_a_round_that_renames_its_item_file' subprojects/docket/tests/test_cli.py
---

**Problem.** vcs._modified_by misses a design round that renames its item's file: git log --name-only reports only a rename's destination, which the commit's parent never held, so PL-VYSP's promotion reads the round as a capture - and the test fake lists both paths, so test_a_round_that_renames_the_item_file_still_claims_it passes against a git that does not behave that way

**Found 2026-09-22 by `PL-8FJK`'s session, measured rather than argued.** In a
scratch repository on git 2.43.0, a commit that `git mv`s an item file and
edits it prints only the destination under `git log --name-only`, because
rename detection is on by default. So `_Walk.own_edits` holds `(new_path,)`,
`_modified_by` asks `<commit>^:<new_path>`, the parent never held that path,
and the round reads as a capture that created its file - the design round is
not promoted. `_modified_by`'s docstring ("a round that renames the item's file
changes two, and the one it inherited is the evidence") describes the fake in
`subprojects/docket/tests/test_vcs.py`, which lists both paths, not git. 40 of
the 992 commits touching `docs/items/` on `origin/main` renamed an item file.
Two directions, neither measured: ask whether the parent held any file for the
*id*, or run the walk with `--no-renames` - which would also hand `_superseded`
the deleted old path, where a removals-only diff reads as superseded. The
closure and queue-only promotions do not call `_modified_by`, so only
`PL-VYSP`'s is affected.

**Reproduced 2026-09-23**, in a scratch repository on git 2.43.0. One commit
`git mv`s `docs/items/PL-K7QX-do-the-thing.md` to
`...-three-items-not-eight.md` and edits it, which git scores as `R061`. Under
`git log --name-only` it lists only the destination. Under `--no-renames` it
lists both paths. `_modified_by`, called with the real runner `_run_git` on the
path the walk records, returns `False`. Handed both paths, as the fake lists
them, it returns `True`. The fake is wrong in two ways. `_runner` lists both
paths for the commit. It also answers `<commit>^:<path>` by the item's *id*,
not by the path, so the test would pass even if it listed only the destination.
From neither side can it fail on this defect.

**How often it can bite, counted on `origin/main`.** 41 of the 1,004 commits
touching `docs/items/` delete a file and add one for the same id; that is the
capture's "40 of 992". Git pairs only 25 of them as renames at its default 50%
similarity. The rest are rewrites, which it lists as a deletion and an
addition, so `--name-only` prints both paths and `_modified_by` reads them
correctly. None of the 25 renames started from a `needs-decision` copy. Four
rounds did rename a `needs-decision` item's file (`PL-4FBP`, `PL-HWW1`,
`PL-J2TD`, `PL-026`), and all four were rewrites. `main` holds squashes, so
the case that bites is hidden from this count: a round whose *newest* branch
commit is a light retitle. Zero is the floor that can be measured, not a
proof.

**Why it matters.** When it bites, `docket next` offers an item that a live
design round holds, and says nothing. That is the failure `PL-VYSP` was built
to stop. The test is the more certain harm. It certifies a behaviour git does
not have, and `_modified_by`'s docstring repeats the claim, so a reader and the
suite both believe renames are covered. The floor in
`.claude/rules/apparatus-standard.md` is that an answer must be true or say
what it could not read. Ranked `P3` on the count above.

**Where the test goes.** `test_vcs.py` says in its module docstring that it
asserts filtering with git injected. Whether git's own output takes the shape
the walk parses is proved against a real checkout in `test_cli.py`.
`test_flight_ignores_a_branch_that_only_wrote_to_the_queue` is the precedent
there, built with `_flight_repo`, and a rename is exactly that half.

**Done when.** On a real checkout, a round whose newest queue-only commit
renames and edits its item's file is in flight while the base holds the item at
`needs-decision`. `test_flight_claims_a_round_that_renames_its_item_file` in
`subprojects/docket/tests/test_cli.py` drives that case. The fake behind
`test_a_round_that_renames_the_item_file_still_claims_it` lists what git lists
and answers the parent read by path. `_modified_by`'s docstring describes what
the code asks.

**Generator check.** A re-entry. `PL-VYSP` (closed 2026-09-19) built
`_modified_by` and pinned the rename case with a fake that could not fail, so
its fix never covered what its docstring claims. It reaches `PL-8FJK`'s family
through `PL-VYSP`, but it is a defect inside an existing shape's test, not a
new unclaimed shape. The underlying fact is a fake that models git's rename
output wrongly, and no other open item shares it. `PL-3LLZ` is about the
fakes' duplication, which is a different mechanism.
