---
id: PL-GL95
title: Nine owner-attribution markers carry no date, so CLAUDE.md's pre-2026-09-16 reading rule cannot classify them at all
status: untriaged
added: 2026-09-20
---

**Problem.** Nine owner-attribution markers carry no date, so CLAUDE.md's pre-2026-09-16 reading rule cannot classify them at all

**Why it matters.** `PL-7RYB` settled on 2026-09-20 that the *date* is what
says whether a plain `(project owner, DATE)` marker records a kind: from
2026-09-16 it means specified, and dated earlier it records no kind at all and
is read as unrecorded. That reaches all 235 dated attributions at the cost of
one clause precisely because every one of them carries a date. Nine do not, so
the rule cannot classify them, and a session meeting one falls back to the
ambiguity the rule was written to remove.

**The nine, found 2026-09-20 by `\(project owner[,)][^)]*\)` filtered for the
absence of a year** (template text in `CLAUDE.md`, `PL-QNMM`, `PL-XWH4`,
`PL-4MPJ` and `PL-7RYB` excluded - those spell `DATE` deliberately):

- `ROADMAP.md:388` - `(project owner, ratified, on \`PL-KQHN\`)`
- `ROADMAP.md:390` - `(project owner, on \`PL-RKWB\`)`
- `ROADMAP.md:1526` - `(project owner, on \`PL-RKWB\`)`
- `ROADMAP.md:4588` - `(project owner, queue item PL-ZMRT)`
- `docs/WORKING_NOTES.md:1697` - `(project owner, on \`PL-NMTF\`)`
- `docs/items/PL-YXXG-…:69` - `(project owner, same day)`
- `docs/items/PL-ZX12-…:104` - `(project owner, same day)`
- `docs/items/PL-16ZC-…:18` - `(project owner, delegating the call)`
- `docs/items/PL-4FBP-…:301` - `(project owner, ratified)`

**Most of them are decidable rather than lost, which is why this is small.**
Seven name an item or say "same day", so the date is recoverable from the named
item's `closed` or the surrounding entry rather than guessed - and two already
carry `ratified`, so only the date is missing from those. `PL-4FBP`'s bare
`(project owner, ratified)` and `PL-16ZC`'s `(project owner, delegating the
call)` are the two that need the surrounding prose read.

**Not fixed in the session that found it** because seven of the nine sit in
`ROADMAP.md` and `docs/WORKING_NOTES.md`, outside `PL-7RYB`'s `touches`, and
because supplying a date means reading each marker's context rather than
applying a rule - which fails two of `CLAUDE.md`'s three fix-now tests.

**Done when.** Each of the nine either carries a date recovered from its own
context, or is listed in the item as genuinely unrecoverable, so that
`CLAUDE.md`'s pre-2026-09-16 rule has a date to read on every attribution in
the tree. `PL-QNMM` is the adjacent sweep of the 52 *dated* but unmarked
attributions in `ROADMAP.md` and `docs/MODEL.md`; this is the smaller,
different problem of markers a date-keyed rule cannot see at all.
