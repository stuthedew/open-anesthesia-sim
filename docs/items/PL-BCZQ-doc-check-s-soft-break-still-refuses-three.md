---
id: PL-BCZQ
title: doc_check's SOFT_BREAK still refuses three kinds of line that continue a paragraph - an ordered list marker other than 1, a pipe line with no delimiter row under it, and a block opener indented four or more columns - and LINK_TITLE cannot cross a line ending after a backslash in a link title, so every pattern read through _statement_matches stops inside a statement statement_lines continues: a closed quotation is refused as unclosed, a link's missing target and a wrapped bold title go unread; live in form
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-10
closed: 2026-10-10
pr: 1392
payoff: a citation, quotation, link or bold title wrapped onto a line opening with a number, a pipe or deep indentation is read whole, as every renderer reads it, so its target is held to the tree
verify: grep -qF '"soft break, a line opening with an ordered marker past 1 continues its quotation"' tests/unit/test_doc_check.py && grep -qF '"soft break, a pipe line continues its quotation"' tests/unit/test_doc_check.py && grep -qF '"links, a title continued after a backslash"' tests/unit/test_doc_check.py
---

**Problem.** doc_check's SOFT_BREAK still refuses three kinds of line that continue a paragraph - an ordered list marker other than 1, a pipe line with no delimiter row under it, and a block opener indented four or more columns - and LINK_TITLE cannot cross a line ending after a backslash in a link title, so every pattern read through _statement_matches stops inside a statement statement_lines continues: a closed quotation is refused as unclosed, a link's missing target and a wrapped bold title go unread; live in form

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditors of
both halves of `tools/doc_check.py`.
`_statement_matches` now bounds each match by the statement `statement_lines`
reads, but inside it `SOFT_BREAK` still refuses the lines
`docket.roadmap.CONTINUED_LINE` refuses: an ordered marker past 1 or with no
content, a pipe line, and any block opener indented four or more columns.
CommonMark 0.31.2 lets only an ordered list starting at 1 interrupt a paragraph
(§ 5.2, § 5.3), GFM 0.29 makes a pipe line a table only over a delimiter row
(§ 4.10), and an indented code block cannot interrupt a paragraph (§ 4.4), so
each such line is paragraph continuation text (§ 4.8). `PL-2S1G` kept the
refusals on the grounds that `statement_lines` reads that context, and
`PL-V7CG` moved `_gate_groups` alone onto it. Separately, `LINK_TITLE`'s three
branches take no backslash followed by a line ending, where § 6.3 lets a title
span lines and keeps the backslash literal.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against markdown-it-py 4.2.0 and cmark-gfm 0.29 (`cmarkgfm`), which
read each input below as one paragraph with the quotation closed, the link
present and the bold run whole:

```text
The rule is written in § "Released on the third of October
2026. Notes follow", which holds it.
See [the notes of
2026. Here](missing-file.md) for more.
**The heading decided in October
2026. Applies.** Text.
See § "A heading with a
| pipe" now.
See [the notes](missing.md "a title ending in a backslash\
and going on") here.
```

`check_citations` reports the first quotation as one its paragraph never
closes, with a remedy that cannot be taken; `LINK_RE` matches neither link, so
both missing targets pass; `_headings` lacks the bold title, so a citation of
it is reported as naming a section nobody wrote; the pipe form reads as
unclosed. The same refusal reaches `QUOTED_SOURCE_RE`, `ITEM_SECTION_RE`,
`UNMARKED_CITATION_RE`, the two version-claim patterns, `declares_none`,
`NOT_DELEGABLE_COUNT_RE`, `MARKER_RE`, `mentions` and
`possessive_section_check.POSSESSIVE_RE`.

Live in form: five such continuation lines stand in the documents and live
briefs `doc_check` reads (in `ROADMAP.md`, `docs/MODEL.md`,
`subprojects/docket/README.md` and two briefs), and a copy whose `SOFT_BREAK`
crosses them gives the same errors, advisories and declines on today's tree.
No titled link stands in the documents.

**Why it matters.** `check_citations`, `check_quoted_sources` and the
close-out sweep's `mentions` are the readers that hold a cited section, a
quotation and a link to the tree, and each crosses a line through `SOFT_BREAK`.
Every renderer reads a line these three forms open as the paragraph's own text,
so a correct citation wrapped onto one is refused with a remedy that cannot be
taken, and a link or bold title wrapped onto one is never read, so its missing
target, or a citation of it, passes unchecked.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-2S1G`'s, `PL-V7CG`'s and `PL-Z1R7`'s fixes
left, and `LINK_TITLE` the gap `PL-KT0H`'s left.

**Done when.** Inside a statement `statement_lines` reads, every pattern built
on `SOFT_BREAK`, `GAP` and `QUOTATION_CHAR` crosses each line ending the
statement continues across, and `LINK_TITLE` crosses one after a backslash;
each form above is a `CONTINUED_STATEMENTS` case that fails on today's readers.


**Built 2026-10-10 (`#1392`).** `SOFT_BREAK` reads the gap alone - trailing
spaces or tabs, the line ending, and the next line's indent and block quote
markers - and refuses no line, since every reader built on it matches within
one statement `statement_lines` cuts, which decides where the paragraph ends. A
link title is read by `_title_end`, which steps over a backslash and the
character after it, a line ending included. `roadmap.CONTINUED_LINE`, which held
the refusals, had no reader left and was removed. Six cases in `PL-R417`'s
guard, the three this brief names and the indented opener, the wrapped link and
the bold title above, each failing on main's readers; and
`tests/unit/test_inline_reference.py` holds the soft break to markdown-it-py
over the specification examples and every tracked document.
