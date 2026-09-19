---
id: PL-Y5JX
title: An item's touches may name another item's file path, so acting on the stale-slug rename advisory would silently break it - PL-3V6C names two
status: untriaged
added: 2026-09-19
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
