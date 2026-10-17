---
id: PL-Q8LJ
title: doc_check's check_quoted_sources tests a quotation against the cited file collapsed into one string, so a quotation spliced from a heading and the paragraph under it, or from two paragraphs, passes as words the file holds; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
milestone: v0.5.25
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-17
pr: 1475
payoff: a claiming citation passes only on words one block of the cited file holds together, so a splice across a heading or a paragraph break cannot stand in for a quotation
verify: grep -q 'def test_a_quotation_spliced_across_a_heading_and_its_paragraph_is_not_in_the_file' tests/unit/test_doc_check.py
---

**Problem.** doc_check's check_quoted_sources tests a quotation against the cited file collapsed into one string, so a quotation spliced from a heading and the paragraph under it, or from two paragraphs, passes as words the file holds; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`tools/doc_check.py`'s middle part.
`check_quoted_sources` asks whether the quoted words stand in the cited file
after `_comparable` normalizes it, and `_normalized` collapses the whole file's
whitespace, so the containment test runs across every statement end the file
has. CommonMark 0.31.2 makes a heading and the paragraph under it two blocks
(§ 4.2, § 4.8), so no quotation of the file's words crosses between them.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against markdown-it-py 4.2.0 and cmark-gfm 0.29, which read the
source as a heading and a separate paragraph:

```text
SRC.md:
## Known limitations

The model ignores shunt.

citing document:
`SRC.md`'s "Known limitations The model ignores shunt" is the source.
```

The quotation passes. Latent: of the 507 quotations that pass today, none
depends on crossing a statement end in its source.

**Re-confirmed 2026-10-11** on main at `16a20a4f`, under python3 3.13.16: the
citing document above passes `check_quoted_sources` silently, while the same
citation quoting "Known limitations Nope" is refused, so the containment test
runs across the heading's end.

**Why it matters.** A claiming citation is the tree's promise that the cited
file holds those words. Spliced across a block boundary, the quotation is
words no reader of the file meets together, and a heading renamed or a
paragraph moved can leave such a splice passing while the sentence it
supported has gone. Latent, so no answer is wrong today.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It reads the
whole text as one statement - the direction
`PL-BYJ5` and `PL-T73L` fixed on the quoting side.
Latent, so an ordinary item under `PL-R417`'s spent head.

**Done when.** A quotation passes only where one statement of the cited file
holds it (a soft break inside that statement still crossed), with a test on
the form above.

**Built 2026-10-17.** `check_quoted_sources` tests a quotation against
`_comparable_statements`: each statement of the cited file, as
`docket.markdown.statement_lines` and the front matter's reader cut it, on a
line of its own, and each fence read whole, since a fence is no statement but
its words are the file's. The form above is refused; a quotation wrapped across
a soft break and one of a fence's lines still pass, and all of the tree's
quotations still pass.
