---
id: PL-9TZH
title: doc_check's _without_code blanks MATH_SPAN_RE's matches a physical line at a time before code spans are read per statement, so a dollar-backtick that a code span opened on the line above has claimed is taken for a well-formed math span and the literal debris CommonMark leaves on the page is never reported; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** doc_check's _without_code blanks MATH_SPAN_RE's matches a physical line at a time before code spans are read per statement, so a dollar-backtick that a code span opened on the line above has claimed is taken for a well-formed math span and the literal debris CommonMark leaves on the page is never reported; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`tools/doc_check.py`'s third part.
`check_math_delimiters` reads `_without_code`'s text, which blanks math spans
line by line with `MATH_SPAN_RE` and only then reads code spans per statement.
A code span runs across a line ending (CommonMark 0.31.2 § 6.1), so a backtick
string opened on the line above can close on the backtick of a math span's
opening dollar-backtick.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against cmark-gfm 0.29, which renders a code span holding the line
break and the dollar, and leaves the rest as literal text:

```text
The `cmd
--opt $`x`$ here.
```

`_without_code` gives the second line with the span blanked and no
`MATH_EDGE_RE` hit, so the literal backtick and dollar on the page are not
reported. Latent: of 875 math spans in tracked Markdown, none follows an odd
backtick run on an earlier line of its statement.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-Z8RS`'s fix left: code spans moved to a
statement at a time, math spans did not.

**Done when.** Math spans are read after code spans and within the statement
both belong to, so the form above reports its debris; a test pins it.
