---
id: PL-Z8RS
title: doc_check's _without_code and _marks_code read code spans a line at a time, so on a line a wrapped span closes, its closing run pairs with the next span's opening run and the prose between reads as code: a TeX delimiter there goes unchecked, and a word there is listed as code
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
payoff: a TeX delimiter in prose after a code span wrapped across lines is checked instead of silently read as code
verify: grep -q 'def test_without_code_reads_a_span_wrapped_across_lines' tests/unit/test_doc_check.py
---

**Problem.** doc_check's _without_code and _marks_code read code spans a line at a time, so on a line a wrapped span closes, its closing run pairs with the next span's opening run and the prose between reads as code: a TeX delimiter there goes unchecked, and a word there is listed as code

**Found 2026-10-03** by `PL-9L39`, which moved both readers onto `docket.release.CODE_SPAN_RE` and left them reading one line at a time, as they read before. Against the document-level reading, `_marks_code` still misreads 1,061 of 133,251 words on the lines of `doc_check`'s documents that hold a backtick, most of them on a line a wrapped span closes. `_without_code` misreads the same lines, and there the miss is silent: a `\(` in the prose between the closing run and the next span is blanked, so the math check never reads it. `doc_check._code_spans` already reads a document's spans whole, so the likely fix maps its spans onto lines for both readers, with `_without_code` blanking math spans first as it does now. `docket new` matched this to `PL-Q9LK` on its title: a different fact, a workflow's shell script, read a line at a time by the same tool.

**Reproduced 2026-10-03 at triage.** On a two-line passage whose first line
opens a code span that the second line closes, followed on the second line by
a TeX `\(x\)` in prose and then another code span, `_without_code` blanks the
prose between the closing run and the next opening run, the delimiter
included, so the math check never reads it.

**Why it matters.** The silent half is a check whose guarantee is void on those
lines: a stray TeX delimiter in prose after a wrapped span closes passes the
math-delimiter check. The louder half is `_marks_code`, which misreads 1,061
words the same way.

**Done when.** `_without_code` and `_marks_code` read a document's code spans
whole, as `doc_check._code_spans` does, so a wrapped span's closing run pairs
with its own opening run, and a test pins a TeX delimiter in prose after a
wrapped span's close as one the math check reads.

**Generator check.** An instance of `PL-KGYT`'s fact, filed after that head
closed on 2026-10-01: two readings of where a code span is, per line and per
document, inside one tool. Filed by `PL-9L39`, a KGYT member whose fix moved
both readers onto `CODE_SPAN_RE` and kept the per-line reading, so a residual
of that fix rather than a re-entry. With `PL-P72R`, the second post-close
instance, which `PL-74T0` reads as its cluster 1.

**Generator check, 2026-10-04.** Also a member of `PL-R417`, with two causes:
the per-line reading is a second spelling of where a code span is, which is
`PL-KGYT`'s fact above, and that spelling is wrong because CommonMark § 6.1 lets
a span continue across lines, which is `PL-R417`'s. Both heads' fixes are the
one this brief already names - read the spans `doc_check._code_spans` reads -
so this item still counts in `PL-74T0`'s cluster 1.
