---
id: PL-Q80R
title: release.code_spans does not step over an autolink or raw HTML opening before a backtick, which doc_check's _InlineReader does, so on <http://a`b> and `c` it reads one span, 'b> and ', where CommonMark and the inline reader read 'c' (found fixing PL-T3GW)
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/release.py, tools/doc_check.py, subprojects/docket/tests/test_markdown_reference.py, subprojects/docket/tests/test_release.py, subprojects/docket/tests/test_verify.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
payoff: docket and the tools find the same code spans CommonMark does where an autolink or a tag holds a backtick, so a cited path is checked and a title escaped by what renders, with one answer where there were two
verify: grep -q 'def test_an_autolink_or_raw_html_opening_first_takes_the_backtick_inside_it' subprojects/docket/tests/test_release.py && grep -q 'def test_a_comparison_shaped_like_a_tag_is_still_read_as_code' subprojects/docket/tests/test_verify.py && ! grep -qF 'which `code_spans` does not read' subprojects/docket/tests/test_markdown_reference.py
reenters: PL-5DZ8
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

**Reproduced 2026-10-17, at triage**, with the title's own text and a raw HTML
twin: on `` <http://a`b> and `c` `` `release.code_spans` reads one span,
`b> and `, where `doc_check._InlineReader` reads `c`; on
`` <span title="`x">y</span> and `c` `` it reads `x">y</span> and ` where the
inline reader reads `c`. The comment above `CODE_SPAN_PATTERN` states the
departure in so many words, and
`test_code_spans_finds_each_specification_example_span_markdown_it_py_finds`
passes over every text holding an autolink or raw HTML to keep it out of the
comparison. Latent: comparing the two readers paragraph by paragraph over every
tracked Markdown file, 789 paragraphs hold a `<` and a backtick and two
disagree - this item's own front matter, which quotes the case, and an HTML
*block* in `PL-2B0B`'s brief, which is that item's (block-level HTML, not an
inline opener). No open item duplicates this; `PL-2B0B` is the nearest.

**Why it matters.** `code_spans` is the one scan of code spans for docket and
`tools/`: `doc_check._code_spans` reads cited paths and test names through it,
`markdown_title` decides what to escape in a title by it, and `checks` and
`picks` blank literals with it. Where an autolink or a tag holds a backtick,
each of those reads the wrong text as code and the real span as prose, while
`doc_check`'s own inline reader, in the same tool, reads it right - two answers
to where a span opens, which is what `one-answer` exists to leave one of.

**Done when.** `release.code_spans` and `release.replace_code_spans` step over
an autolink or raw HTML that opens before a backtick, as CommonMark 0.31.2
§ 6.1 gives, reading `AUTOLINK_RE` and `RAW_HTML_RE` from `docket.release`,
where they move and `tools/doc_check.py` imports them, so one copy of each
remains. `verify.NON_CODE_RE` is left reading Python as it does now: it takes
`CODE_SPAN_PATTERN` into its alternation, and `RAW_HTML_RE` matches
`<b and c>` in `if a<b and c>d:`, so the step-over must not reach the pattern
verify blanks with. `subprojects/docket/tests/test_release.py` gains
`test_an_autolink_or_raw_html_opening_first_takes_the_backtick_inside_it`, over
the two texts above; `subprojects/docket/tests/test_verify.py` gains
`test_a_comparison_shaped_like_a_tag_is_still_read_as_code`, pinning
`strip_non_code` on that line; and the reference test passes over a link or an
image only, with the docstring sentence saying `code_spans` does not read an
autolink or raw HTML deleted.

**Generator check, answered 2026-10-17.** The fact is `PL-5DZ8`'s - which
spelling of a repeated predicate is the answer, here where a code span may
open - and `PL-5DZ8` closed `spent` at 00:52 UTC on 2026-10-12, twenty-one hours
before this was filed at 21:59 UTC, so this is an **instance of that head's
fact filed after it closed**, recorded as `reenters: PL-5DZ8` (its sweep read
the comment that named the case, and should have covered it). It does **not**
reopen the head's `spent`. It is the head's second post-close re-entry, beside
`PL-4S6C`, and the store's rule for a fix that did not hold is three. And it is
no new reader written since the close: `PL-T3GW`'s fix wrote the departure
down beside the escape it did take, and this item was filed in that same
commit, so it is a known remainder of the sweep rather than a mechanism still
handing out members. `PL-4S6C`, the successor head, says a member of this kind
- two readers of one fact touching no primitive, which `fact_home_check` cannot
see - is evidence for a new head rather than for it; one item is not a head.
