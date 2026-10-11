---
id: PL-4CJ8
title: Four comments cite CommonMark 0.31.2 § 6.7 for a soft break, where 0.31.2 numbers soft line breaks § 6.8 and § 6.7 is hard line breaks - statement_lines' docstring, the comment above docket.roadmap's CONTINUED_LINE, and a comment each in test_roadmap and PL-R417's guard - so a reader checking the citation lands on the wrong rule
priority: P3
effort: S
status: ready
classes: docs
touches: subprojects/docket/src/docket/markdown.py, subprojects/docket/tests/test_roadmap.py, tests/unit/test_doc_check.py
added: 2026-10-06
payoff: A reader checking a soft-break citation against CommonMark lands on the soft-break rule rather than the hard-break one
verify: grep -qF '(§ 6.8) and a lazy continuation' subprojects/docket/src/docket/markdown.py && grep -qF '(0.31.2 § 6.8)' subprojects/docket/tests/test_roadmap.py && grep -qF '§ 6.8) and a code span' tests/unit/test_doc_check.py
---

**Problem.** Four comments cite CommonMark 0.31.2 § 6.7 for a soft break, where 0.31.2 numbers soft line breaks § 6.8 and § 6.7 is hard line breaks - statement_lines' docstring, the comment above docket.roadmap's CONTINUED_LINE, and a comment each in test_roadmap and PL-R417's guard - so a reader checking the citation lands on the wrong rule

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), checking the
sections the sweep's own briefs cite against the CommonMark 0.31.2 spec text.
Its inlines are numbered code spans (§ 6.1), emphasis, links, images,
autolinks, raw HTML (§ 6.6), hard line breaks (§ 6.7) and soft line breaks
(§ 6.8). Four places say a paragraph goes on across a soft break and cite
§ 6.7: the docstring of `statement_lines` in
`subprojects/docket/src/docket/markdown.py`, the comment above `CONTINUED_LINE`
in `subprojects/docket/src/docket/roadmap.py`, a case comment in
`subprojects/docket/tests/test_roadmap.py`, and the comment above
`CONTINUED_STATEMENTS` in `tests/unit/test_doc_check.py`. The fifth, the
comment above `SOFT_BREAK` in `tools/doc_check.py`, was corrected on the
sweep's branch as a fix in passing. Four closed items' briefs carry the same
number, and are records of the tree their work was done against.

**Reproduced 2026-10-11** on main at `16a20a4f`: three of the four still cite
§ 6.7 for a soft break - `statement_lines`' docstring in `markdown.py`, the first
case comment under test_roadmap's "where a Markdown statement ends" section,
and the comment opening `PL-R417`'s guard section in `test_doc_check.py` - and
the copy of the spec under `tests/unit/markdown-specs/` orders its Inlines
chapter code spans, emphasis, links, images, autolinks, raw HTML, hard line
breaks, soft line breaks, so § 6.7 is hard line breaks. The fourth, the comment
above `roadmap.py`'s `CONTINUED_LINE`, went with that constant in #1392
(`1ee4e78e`); `doc_check.py`'s `SOFT_BREAK` comment cites § 6.8.

**Why it matters.** A citation is how a reader checks a reader's rule against
the spec, and these send a reader to the rule for a backslash or two-space line
ending where they mean a plain one. A session following one lands on the wrong
rule and may "correct" code that is right.

**Generator check.** Not a member of `PL-R417`: a wrong citation, copied from
one comment to the next.

**Done when.** The four cite § 6.8. Since #1392 three remain, the ones the
reproduction names.
