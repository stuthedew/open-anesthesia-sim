---
id: PL-Y7BS
title: ROADMAP.md's v0.5.3 row holds an unescaped pipe inside a code span, so GitHub's table cuts the row there and shows 1 of its 13 item ids, while docket's checks read all 13
status: dropped
added: 2026-10-10
closed: 2026-10-11
reason: Already fixed: #1392 (1ee4e78e, 2026-10-10) escaped the v0.5.3 row's pipe, so GitHub renders all 13 ids, and docket.markdown.cells already splits a row where GFM 0.29 does (PL-5NC3, #1358), pinned by test_doc_check's escaped-pipe case; re-measured 2026-10-11 at 16a20a4f.
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

**Re-measured 2026-10-11** on main at `16a20a4f`: the premise no longer holds.
`#1392` (`1ee4e78e`, 2026-10-10) escaped the pipe as `\|`, and markdown-it-py
4.2.0's GFM table now renders 13 of the row's 13 ids. `docket.markdown.cells`
already splits a row at every pipe no backslash escapes, inside a code span or
not, as GFM 0.29 § 4.10 does (`PL-5NC3`, `#1358`), and
`tests/unit/test_doc_check.py`'s case "table rows, an escaped pipe inside a
cell" pins it: with the escape removed again, docket's cells and markdown-it-py
both read 1 id in the row. Both halves of **Done when.** already hold.
