---
id: PL-Q80R
title: release.code_spans does not step over an autolink or raw HTML opening before a backtick, which doc_check's _InlineReader does, so on <http://a`b> and `c` it reads one span, 'b> and ', where CommonMark and the inline reader read 'c' (found fixing PL-T3GW)
status: untriaged
touches: subprojects/docket/src/docket/release.py, tools/doc_check.py, subprojects/docket/tests/test_markdown_reference.py
added: 2026-10-12
---

**Problem.** release.code_spans does not step over an autolink or raw HTML opening before a backtick, which doc_check's _InlineReader does, so on \<http://a`b> and `c` it reads one span, 'b> and ', where CommonMark and the inline reader read 'c' (found fixing PL-T3GW)

**Found 2026-10-12 while fixing `PL-T3GW`** (`#1464`), which made
`release.code_spans` the one scan of code spans for docket and `tools/` and
had it step over a backslash escape as CommonMark 0.31.2 § 6.1 does. The same
section gives an autolink or raw HTML that opens first the backtick inside
it; `doc_check`'s `_InlineReader` reads that, and `code_spans` does not.
Reproduced on that branch: on the text above, `code_spans` returns one span
whose content is `b> and `, and `_InlineReader` returns `c`. Moving
`AUTOLINK_RE` and `RAW_HTML_RE` beside the scan in `docket.release`, and
dropping the reference test's pass over texts holding them, would close it.

**Not a recurrence of `PL-9TZH`**, which `docket new` matched it to by title:
that item is the order math spans and code spans are blanked in.

**Generator check.** The fact `PL-5DZ8` names - which spelling of one predicate
is the answer - and a remainder of its sweep rather than a new reader: the
comment on `doc_check`'s `SPAN_AT` that the sweep read named this case beside
the escape, and only the escape was filed. Whether that reopens the head's
`spent` is triage's to weigh.
