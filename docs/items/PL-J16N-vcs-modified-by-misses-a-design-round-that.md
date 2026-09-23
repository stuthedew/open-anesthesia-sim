---
id: PL-J16N
title: vcs._modified_by misses a design round that renames its item's file: git log --name-only reports only a rename's destination, which the commit's parent never held, so PL-VYSP's promotion reads the round as a capture - and the test fake lists both paths, so test_a_round_that_renames_the_item_file_still_claims_it passes against a git that does not behave that way
status: untriaged
feature: parallel-sessions
added: 2026-09-22
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
