---
id: PL-4LT9
title: bin/docket verify <id> audits the whole batch branch, because item_commits matches every commit subject and CLAUDE.md requires every subject to lead with every id it closes
status: untriaged
added: 2026-09-12
---

**Problem.** bin/docket verify <id> audits the whole batch branch, because item_commits matches every commit subject and CLAUDE.md requires every subject to lead with every id it closes

**Observed 2026-09-12** on `PL-3B47`'s branch, which closed nineteen items.
`bin/docket verify PL-ZWBK --base origin/main` reported ten paths outside
`touches` - `Makefile`, four other items' files, and four `subprojects/docket`
source and test files - none of which is `PL-ZWBK`'s work. All of them are the
*branch's* work.

**Mechanism.** `item_commits` selects the branch commits whose subject matches
the id, and `CLAUDE.md` requires a commit closing several items to lead with
**all** of them. On a batch branch every subject therefore names every id, so
the selection is the whole branch for any id you ask about, and the per-item
scoping that `item_commits`' own docstring promises - "a reviewer can take four
items and reject the fifth" - does not happen.

**Why it matters.** The command is the close-out audit this project asks a
session to run on its own branch, and on a batch branch it cannot distinguish
one item's overreach from another item's declared work. Every result is a
`REJECT` naming paths that are legitimately declared somewhere, which is the
"fires on correct work" shape `CLAUDE.md` names as a defect in a check.

**Not the same as `PL-69JZ` or `PL-66PR`.** Those are audits that refuse a
*sanctioned* edit; this is the commit selection being wrong about which edits
belong to the item at all, so it survives any exemption added to the audits.

**Approach, undecided.** The honest options look like: verify a *set* of ids
together and union their `touches`, which is what a batch branch actually
commissions; or scope by the diff of the commit that closes the item rather
than by every commit naming it; or state that `docket verify` answers only for
a single-item delegated branch and have it say so when it finds a commit naming
ids other than the one asked about. The last is cheapest and may be enough.
