---
id: PL-NGKW
title: docket's vcs._markdown_statements compares a GFM table row, and a run of indented code, as a statement of its own outside the block that holds it, so a ref that moves a row into the table above - or joins two code runs - reads as holding nothing more than the base, and stranded and superseded drop an edit that changed what a table says; live in form
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
milestone: v0.5.23
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/markdown.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-10
closed: 2026-10-10
pr: 1392
payoff: an edit that moves a row into a table or joins two code runs reads as the change it is, so stranded and superseded keep it
verify: grep -qF '"superseded, two tables joined into one"' tests/unit/test_doc_check.py && grep -qF '"superseded, two code runs joined into one"' tests/unit/test_doc_check.py && grep -qF '"standing, two tables joined into one"' tests/unit/test_doc_check.py
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

**Why it matters.** `stranded` and `_superseded` decide whether a
branch's edit still has to land; one read as holding nothing more than the base
is left off the stranded report and can be deleted with its branch. Adding a row
to a table changes what the table says, and item files are full of tables, so
the edit this misreads is one a session is likely to make.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-F7Z6`'s fix left.

**Done when.** A statement is compared with its block's kind and the block it
belongs to - a table whole, a code block whole - so each form above reads as
outstanding; a test pins each.

**Built 2026-10-10 (`#1392`).** `vcs._markdown_statements` reads a body
statement as a leaf block `markdown.read` reads, whole and tagged with its kind,
rather than as a span of `markdown.statement_lines`: a table is one statement
across all its rows, and an indented code block one with the blank lines inside
it, so a table row and a paragraph of the same text are no longer one
statement. A ref that cuts the lines between two tables, or two code runs, or
the blank line between a table and a paragraph, holds a block the base never
held, so `_superseded` keeps the path outstanding and `_standing` reads the copy
as ahead. A whole table cut is still superseded. Five cases in `PL-R417`'s
guard; the four forms above fail on main's reader.
