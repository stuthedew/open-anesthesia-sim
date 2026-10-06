---
id: PL-4CJ8
title: Four comments cite CommonMark 0.31.2 § 6.7 for a soft break, where 0.31.2 numbers soft line breaks § 6.8 and § 6.7 is hard line breaks - statement_lines' docstring, the comment above docket.roadmap's CONTINUED_LINE, and a comment each in test_roadmap and PL-R417's guard - so a reader checking the citation lands on the wrong rule
status: untriaged
added: 2026-10-06
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

**Generator check.** Not a member of `PL-R417`: a wrong citation, copied from
one comment to the next.

**Done when.** The four cite § 6.8.
