---
id: PL-47QV
title: docket verify's 'item front matter unchanged' check can never fail: Item.path is a bare filename, so its git show and its on-disk read both miss and it returns 'unchanged' unconditionally
status: dropped
added: 2026-09-07
closed: 2026-09-12
reason: Already fixed. PL-20PT (v0.4.11) rebuilt this as front_matter_check: it joins items_dir to Item.path, finds the base copy by id rather than by name so a title change cannot move the file out from under the guard, and returns a refusal - not a pass - where the comparison cannot be made at all. Verified 2026-09-12 against subprojects/docket/src/docket/verify.py:370-420. The regression test this item asked for is tests covering that third outcome.
---

**Problem.** docket verify's 'item front matter unchanged' check can never fail: Item.path is a bare filename, so its git show and its on-disk read both miss and it returns 'unchanged' unconditionally

`store.read_items` builds every item with `parse_item(text, path.name)`, so
`Item.path` is `PL-XXXX-slug.md` rather than `docs/items/PL-XXXX-slug.md`.
`verify._front_matter_changed` then runs `git show <base>:PL-XXXX-slug.md`,
which exits non-zero from the repository root, and the function returns `()`
on that non-zero status - the "a new item file has no previous front matter"
branch. Its `(root / item.path)` read misses for the same reason.

Measured 2026-09-07 on the PL-4WQS branch: the item file had `status` moved
`ready` -> `done`, a `closed` date added and `touches` widened, and
`bin/docket verify PL-4WQS` still reported `PASS item front matter unchanged -
unchanged`. Called directly, `_front_matter_changed(root, "origin/main", item)`
returns `()` while `git show origin/main:docs/items/<file>` resolves fine.

This is the silent-wrong-answer shape: the guard reports the reviewer-only
fields were untouched when it never looked. A fix owes a test that changes a
front-matter field and asserts the check fails, since the current check would
pass against any input.
