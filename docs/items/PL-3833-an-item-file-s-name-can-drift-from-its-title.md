---
id: PL-3833
title: An item file's name can drift from its title and nothing checks it, so the store carries a stale slug until some unrelated rewrite happens to fix it
priority: P3
effort: S
status: ready
classes: defect
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-04
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_a_filename_that_does_not_match_its_title_is_reported' subprojects/docket/tests/test_checks.py
---

**Problem.** An item file's name can drift from its title and nothing checks
it, so the store carries a stale slug until some unrelated rewrite happens to
fix it

**Observed 2026-09-04, closing `PL-D4MZ`.** On `origin/main`, `PL-3D2M` was
titled "A commit pushed after its pull request merged lands nowhere..." while
its file was still named
`PL-3D2M-a-pull-request-merged-at-a-stale-head-silently.md` - the slug of a
title it no longer had. `make check` passes on that tree, so nothing in
`docket check` compares the two.

It surfaced only because `bin/docket record` rewrites a whole item file to add
`pr:`, and the store names files from the title, so the rewrite renamed it. That
is `record` behaving correctly; the point is that without an unrelated rewrite
the drift is invisible, and the next session to touch that item gets a rename in
a diff that has nothing to do with renaming.

**Why it matters.** The filename is how a session finds an item by hand - `ls
docs/items/ | grep`, a path in a commit subject, a citation in another item's
brief. A slug describing a title the item no longer has sends that session to
the wrong mental model of what the item is about, or to no file at all. It is
also exactly the decidable kind of check `CLAUDE.md` prefers to put in code:
derive the slug from the title, compare, fail.

**Where.** `subprojects/docket/src/docket/checks.py`, alongside the other
store-integrity checks, using whatever slug function `docket new` and `record`
already share so the check and the writer cannot disagree.

**Done when.** `docket check` fails an item whose filename does not match the
slug its title generates, and `make check` catches the drift on the tree that
has it.

**The "unrelated rewrite" that fixes it is not free, observed 2026-09-08.**
`bin/docket record`, run to write six owed `pr` numbers, re-rendered
`PL-36R4` and renamed its file from the `thirty-eight` slug to `forty-two`,
its title having been changed on `main` while the filename was not. That is
the cure this brief describes, and it arrived attached to a commit about
something else entirely — while `origin/claude/ui-overhaul-planning-avjx5r`
was editing that same file, which makes it a rename-against-edit conflict for
whoever merges second. The rename was backed out of that commit for exactly
that reason.

So a check here has a second job beyond reporting the drift: whatever fixes
one should not fix it as a side effect of an unrelated command, because the
session running that command has no reason to be looking at who else holds the
file. Reporting the drift and leaving the rename to a session that has checked
is the safer split.
