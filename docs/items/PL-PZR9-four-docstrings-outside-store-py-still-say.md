---
id: PL-PZR9
title: Four docstrings outside store.py still say store.write_item renames an item file when its title changes - in verify.py, cli.py's _write_pr, test_verify.py and test_cli.py - though PL-9KSY removed the replace= that did it, and a rename is now git mv's alone
priority: P3
effort: S
status: done
classes: docs
feature: slug-rename-on-write
milestone: v0.5.12
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_cli.py
added: 2026-09-26
closed: 2026-09-26
pr: 1059
payoff: each guard's stated reason matches the code again, so a reader checking one against write_item no longer concludes a live guard is stale
verify: ! grep -qF 'renames the file when the title changes' subprojects/docket/src/docket/verify.py && ! grep -qF 'has drifted it turns one added line into a delete-plus-add' subprojects/docket/src/docket/cli.py && ! grep -qF 'The rename is `store.write_item`' subprojects/docket/tests/test_verify.py && ! grep -qF 'through `write_item` renames it' subprojects/docket/tests/test_cli.py
---

**Problem.** Four docstrings outside store.py still say store.write_item renames an item file when its title changes - in verify.py, cli.py's _write_pr, test_verify.py and test_cli.py - though PL-9KSY removed the replace= that did it, and a rename is now git mv's alone

**Found 2026-09-26, closing `PL-9KSY`** (`store.write_item`'s dead `replace=`
rename branch). `write_item` now writes a new item under the name its title
gives it and removes nothing, so a title edit written through it leaves the old
file beside the new one. Four docstrings outside that item's `touches` still
name it as the thing that renames:

- `subprojects/docket/src/docket/verify.py`, in `front_matter_check`: "The
  base copy is found by id rather than by name, because `store.write_item`
  renames the file when the title changes". The conclusion holds, since a
  `git mv` pass moves the file just as well; the cause it gives does not.
- `subprojects/docket/src/docket/cli.py`, in `_write_pr`: "`write_item`
  derives the filename from the title, so on a file whose slug has drifted it
  turns one added line into a delete-plus-add". Through `write_item` as it
  stands that write is a second file under the same id, which is still a
  reason `record` must not use it.
- `subprojects/docket/tests/test_verify.py`, in
  `test_a_title_edit_that_renames_the_file_is_still_compared_by_id`: "The
  rename is `store.write_item`'s, and the title is front matter."
- `subprojects/docket/tests/test_cli.py`, in
  `test_record_keeps_a_drifted_filename`: "re-rendering a drifted one through
  `write_item` renames it".

**Reproduced 2026-09-26** on `78b1a02b`: all four passages stand as quoted.
`store.write_item`'s docstring now says it "removes nothing" and that "A rename
is a pass of its own, made with `git mv`". Outside the queue, the filing commit
`86b510d9` changed only `store.py` and `test_store.py`, so the work is not
already on the default branch.

**Why it matters.** Each is the reason given for a guard. A reader checking the
reason goes to `write_item`, finds no rename there, and can conclude the guard
is stale when it is not: the rename that matters now is a `git mv` pass
(`PL-YTDN`), and all four guards still stand against it.

**Done when.** Each of the four names the rename it guards against as it now
happens, a `git mv` pass or a title edit landing under a second name, with no
behaviour changed.

**Generator check.** A one-off, which the close-out docs sweep caught as
designed. The fact misread is the link between a document sentence and the
tree fact it restates (`PL-4FBP`, `PL-G424`, both closed 2026-09-19), but
neither head's route claims this kind. `PL-4FBP` leaves a claim outside a
bound family to the close-out sweep "by decision rather than by oversight".
`PL-G424` leaves prose drift that is not a citation to judgment and the
capture rule, on purpose. `doc_check` decides whether a cited path exists,
never whether the sentence around it is still true.
