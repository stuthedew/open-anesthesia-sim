---
id: PL-NGKW
title: docket's vcs._markdown_statements compares a GFM table row, and a run of indented code, as a statement of its own outside the block that holds it, so a ref that moves a row into the table above - or joins two code runs - reads as holding nothing more than the base, and stranded and superseded drop an edit that changed what a table says; live in form
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** docket's vcs._markdown_statements compares a GFM table row, and a run of indented code, as a statement of its own outside the block that holds it, so a ref that moves a row into the table above - or joins two code runs - reads as holding nothing more than the base, and stranded and superseded drop an edit that changed what a table says; live in form

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.vcs`. `_holds_nothing_more` (for
`_superseded`, and through it `orphaned`, `landed_whole` and the claims
reader) and `_standing`'s removal arm (for `stranded` and `_behind_on_base`)
compare Markdown statements in their place, and the place `PL-F7Z6`'s fix
records is the marker lines of the list items holding a statement. A table is
one block across its rows (GFM 0.29 § 4.10, which also continues it at a plain
line right after a row), and the blank lines between chunks of an indented
code block belong to it (CommonMark 0.31.2 § 4.4); the statement tuple records
no block kind, so a row `b` and a paragraph `b` compare equal.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, on scratch repositories, against cmark-gfm 0.29 and markdown-it-py
4.2.0, which read the ref as one table with body rows `a` and `b` under the
first header - a statement the base never held:

```text
base:
| allowed |
| --- |
| a |

| refused |
| --- |
| b |

ref: the three lines between cut, leaving
| allowed |
| --- |
| a |
| b |
```

In an item file, `_superseded` and `_behind_on_base` both name it and
`stranded` reports no edit; the same ref with one line added is reported
stranded. `docket.markdown.read` itself reads the ref as one table. A table
followed by a paragraph `b`, and two indented code runs a paragraph apart,
read the same way. (`statement_lines` also splits an indented code block at
its blank lines differently inside a block quote, the unit the code-run form
compares.)

Live in form: 352 of 2,508 tracked Markdown files - 279 of them item files -
hold a table followed, past blank lines only, by a paragraph or table at the
same depth; no ref in a fresh checkout carries work, so no answer is wrong
today.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-F7Z6`'s fix left.

**Done when.** A statement is compared with its block's kind and the block it
belongs to - a table whole, a code block whole - so each form above reads as
outstanding; a test pins each.
