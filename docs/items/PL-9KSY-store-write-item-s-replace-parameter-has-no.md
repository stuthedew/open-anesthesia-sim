---
id: PL-9KSY
title: store.write_item's replace= parameter has no caller left now that every field write uses rewrite_item, and PL-YTDN's rename pass is specified as git mv, so the rename branch is dead code that the next field writer could still reach for
priority: P3
effort: S
status: done
classes: refactor
feature: slug-rename-on-write
milestone: v0.5.12
touches: subprojects/docket/src/docket/store.py, subprojects/docket/tests/test_store.py
added: 2026-09-19
closed: 2026-09-26
pr: 1048
verify: ! grep -q 'replace: Path | None' subprojects/docket/src/docket/store.py
---

**Problem.** store.write_item's replace= parameter has no caller left now that every field write uses rewrite_item, and PL-YTDN's rename pass is specified as git mv, so the rename branch is dead code that the next field writer could still reach for

**Confirmed against the tree, 2026-09-19.** `grep -rn 'replace=' subprojects/docket`
returns exactly one hit - `subprojects/docket/tests/test_store.py:113` - and no
production caller. `write_item`'s own docstring already routes field writers
away from it: "A command writing a field reaches for `rewrite_item` instead,
whatever it finds the name to be."

**Why it matters.** A rename branch reachable from a function every writer
already calls is the exact hazard `PL-5QLP`, `PL-LBR6` and `PL-QMC0` were
filed for: each was a command renaming an item file as a *side effect* of
writing a field, and each cost a conflict against whoever else was holding that
file. All three are closed and the callers now use `rewrite_item`, so the
defect is gone - but the door it came through is still open and still
documented as the way to write an item. The next writer added to this module
reads `write_item(directory, item)` as the obvious call and gets the rename
branch back for free, with nothing failing to say so. Dead code that reproduces
a closed defect when reached is worth more than dead code that merely sits
there, which is why this is `refactor` rather than tidying.

**Done when.** `write_item` no longer takes `replace=`, the rename path lives
wherever a pass whose *subject* is the rename can reach it, and
`subprojects/docket/tests/test_store.py` no longer exercises the parameter.

**Worked.** Still true on `f8719f71` when picked up: `replace=` had one caller,
`test_store.py`'s rename test, and no production caller. Read "the rename path
lives wherever a pass whose *subject* is the rename can reach it" as `git mv`,
which `PL-YTDN` specified and `docket check`'s stale-slug advisory already
names, so no rename function was added: one would be a new mechanism with no
caller. `test_renaming_removes_the_file_the_item_used_to_live_in` is replaced by
`test_writing_a_new_title_leaves_the_old_file_in_place`, which pins what
`write_item` does now (a title written through it lands beside the old file), so
a delete added back to it fails a test instead of passing silently.
`rewrite_item`'s docstring said `write_item`'s naming "is right when the title
was the edit", which stopped being true with the delete; it now says the naming
is right for a new item. Four docstrings outside `touches` still give a
`write_item` rename as the reason for their guard, and are `PL-PZR9` rather
than edited here.
