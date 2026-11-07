---
id: PL-PNH2
title: ROADMAP.md's timeline does not say what its Size column counts or as of when, whether rows 1 and 2, the v0.4.x track and Gate 3 have shipped or cleared, how v0.5.0's sixteen items square with its 20 ids and undated 185 entries, or what 'Row 11 is the intended order' covers
status: untriaged
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
---

**Problem.** `ROADMAP.md` § "The timeline" leaves four things a reader needs
to read it, and the tree does not settle them. Each was raised as a query by
chapter read 3 of the structure read (`PL-DWGC`, the timeline at rows 439-475
of `aff76df1`), and each needs the author's answer or a count from the
records.

1. The Size column does not say what it counts, or as of when. The v0.4.26
   and v0.6.0 rows give sizes of 2 L, 2 M, 3 S and 4 L, 16 M, 3 S, but say 28
   and 40 Required-scope ids were closed. The v0.5.0 and v0.7.0 rows are
   scoped and show "—", although the horizon table says only rows not yet
   scoped have no size.
2. Some rows do not say whether their step is done. Rows 1 and 2 (v0.2.8 and
   v0.3.0) do not say whether or when they shipped. The `v0.4.x` row does not
   say whether the exact step (`PL-GS5X`) and the naming items have shipped,
   and it keeps the name `v0.4.x` although the interface-pass row says a patch
   track takes the number of the release it follows. The rows from the two
   `v0.6.x` tracks to Gate 3 do not say whether Gate 3, frozen on 2026-10-25,
   has cleared, or whether work on v0.7.0 has begun.
3. The v0.5.0 row says "sixteen items carry it" and "all 20 Required-scope
   ids closed". Its "a list now standing at 185 entries" has no date, while
   the Gate 1 row gives 175 entries on 2026-09-20.
4. The notes under the table say "Row 11 is the intended order" without
   saying whether that means row 11 alone, rows 11 onward, or every row not
   yet scoped. Until this is answered, the notes keep the next sentence, "A
   row becomes real only when it gets its own goal, required scope,
   definition of done and out-of-scope list", although the Near row of the
   horizon table in § "The planning model: a rolling wave" says the same.

**Done when.** The timeline says what Size counts and as of when, and each
row says whether its step is done. v0.5.0's counts are reconciled, or each
says what it counts and when. "Row 11 is the intended order" says what it
covers.

**Generator check.** Queries from one structure read. Nothing produces them,
so nothing is recorded as a generator. `docket new` matched this filing to
`PL-33FM`, which is Gate 0's size, a different count in a different section;
that match is withdrawn.
