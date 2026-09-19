---
id: PL-Y5JX
title: An item's touches may name another item's file path, so acting on the stale-slug rename advisory would silently break it - PL-3V6C names two
priority: P2
effort: S
status: ready
classes: defect
feature: slug-rename-on-write
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-19
verify: grep -q 'def test_touches_naming_a_missing_item_file_is_an_error' subprojects/docket/tests/test_checks.py
---

**Problem.** An item's touches may name another item's file path, so acting on the stale-slug rename advisory would silently break it - PL-3V6C names two

**Found 2026-09-19 closing `PL-4Q9B`** (record clone trust and the permitted
ref operations), which retitled `PL-TFWR` so its title stopped asserting an
unproven cause.

`docket check`'s grooming advisory then named `PL-TFWR` among the item files
"carrying a slug their title no longer generates", and told the reader to
`git mv` it to the name `docket` would write. Acting on that would have broken
`PL-3V6C`, whose `touches` names two item files by full path:

```
touches: docs/items/PL-TFWR-a-session-cannot-delete-a-remote-branch-the-git.md, docs/items/PL-XQRK-a-session-cannot-delete-a-remote-branch-git.md
```

A renamed file leaves that declaration pointing at nothing. `touches` is read by
`bin/docket concurrent`, by the lane split, and by `docket verify`'s
inside-`touches` audit, and all three would answer from a path that no longer
exists - silently, because a `touches` entry naming a missing path is not
currently an error.

**Why it matters is the combination, not either half.** Naming an item file in
`touches` is legitimate and correct: `PL-3V6C`'s whole deliverable was editing
two briefs. The rename advisory is also legitimate. Together they are an
instruction to break a declaration, issued to a reader who has no reason to
look.

**Two candidate fixes, and they compose.** Have `docket check` error on a
`touches` entry that names a path under `docs/items/` which does not exist -
decidable, cheap, and it catches every way the coupling breaks rather than only
the rename. And have the slug advisory say when another item's `touches` names
the file it is proposing to rename, so the reader is told before acting.

**The rename was skipped here** for that reason, and `PL-TFWR` keeps its old
slug deliberately; the closing commit records why. Two of the eight files the
advisory currently names are `PL-TFWR` and `PL-XQRK`, which are exactly the two
`PL-3V6C` declares.

**Superseded in part, 2026-09-19, by `PL-YTDN`** (rename the item files whose
slug no longer matches their title), on a decision the project owner ratified
the same day over leaving `PL-TFWR` drifted behind the skip recorded here.
Ratified rather than specified, so ordinary evidence reopens it: a cost the
case did not carry is enough, and it was a session's own recommendation. That pass renamed `PL-TFWR` after measuring
the coupling, and repaired both declarations in the same commit: `PL-3V6C`'s and
`PL-77SV`'s `touches` now name the new path. So the paragraph above records what
was found on the day, not what is true now, and the live instance this item was
discovered through is gone.

**The guard is still owed, and the reason is stronger rather than weaker.**
`PL-YTDN` only got this right because it went looking - the brief's own re-check
one-liner scans `verify` and the body and *not* `touches`, so it reported no
coupling at all, and the two real declarations were found by hand. That is the
failure this item names, reproduced by the very pass that repaired it. The test
fixture must now be synthetic: build an item declaring two item files by full
path, one of which the advisory wants renamed, rather than reaching for a live
instance.

**Done when.** A `touches` entry naming a path under `docs/items/` that does not
exist is an error from `bin/docket check`, and the stale-slug advisory names any
other item whose `touches` declares the file it is proposing to rename. Both are
decidable from the store, so both are checks rather than prose. A test drives
`PL-3V6C`'s shape: an item declaring two item files by full path, one of which the
advisory wants renamed.
