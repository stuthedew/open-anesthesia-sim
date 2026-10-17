---
id: PL-9TZH
title: doc_check's _without_code blanks MATH_SPAN_RE's matches a physical line at a time before code spans are read per statement, so a dollar-backtick that a code span opened on the line above has claimed is taken for a well-formed math span and the literal debris CommonMark leaves on the page is never reported; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
milestone: v0.5.25
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1472
payoff: a math span whose opening a wrapped code span has claimed is reported as the literal dollar and backtick GitHub shows, rather than passed as well-formed TeX
verify: grep -q 'def test_a_math_span_a_wrapped_code_span_claims_reports_its_debris' tests/unit/test_doc_check.py
recurrences: 2026-10-12 PL-T3GW
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

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`: `_without_code` returns
the second line with the math span blanked and the code span's opening
backtick left on the first, and `MATH_EDGE_RE` finds nothing in its output.

**Why it matters.** `check_math_delimiters` exists so a TeX span GitHub will not
render is caught before it ships as literal dollars and backticks. Here that
debris is on the page and the check reports nothing, which is the one answer
it must not give.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-Z8RS`'s fix left: code spans moved to a
statement at a time, math spans did not. Latent - no tracked file holds the form - so it is an ordinary item
under the spent head, and one found live reopens it.

**Done when.** Math spans are read after code spans and within the statement
both belong to, so the form above reports its debris; a test pins it.
