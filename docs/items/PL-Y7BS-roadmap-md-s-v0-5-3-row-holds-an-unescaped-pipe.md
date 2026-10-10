---
id: PL-Y7BS
title: ROADMAP.md's v0.5.3 row holds an unescaped pipe inside a code span, so GitHub's table cuts the row there and shows 1 of its 13 item ids, while docket's checks read all 13
status: untriaged
added: 2026-10-10
---

**Problem.** `ROADMAP.md`'s row for v0.5.3, at line 103 and 5,045 characters,
holds an unescaped pipe inside the code span that pipes `make check` output to
`tail`. GFM ends a table cell at an unescaped pipe even inside a code span, so
cmark-gfm, which GitHub renders with, cuts the row there: rendered, the row
shows 1 of its 13 item ids. docket's checks read the source and count all 13,
so a reader of the roadmap on GitHub sees a different gate from the one the
checks hold.

**Found 2026-10-10** by the parsing review in `PL-R417`'s closing sweep thread
(link 23), which named it a parser differential: two readers of one table that
disagree on where a cell ends.

**Reproduced 2026-10-10** on the branch at `54f5419b`, whose `ROADMAP.md` is
`main`'s at `75e1700d`: cmarkgfm (cmark-gfm 0.29) rendering the table that
holds line 103 gives 13 item ids in the source row and 1 in the rendered row.

**Generator check.** Not a member of `PL-R417`: where a cell ends within one
line, not where a statement ends across lines.

**Done when.** The row's pipe is escaped, so GitHub shows all 13 ids, and
docket reads a table row's cells where GFM does, or refuses such a row by
name, pinned by a test.
