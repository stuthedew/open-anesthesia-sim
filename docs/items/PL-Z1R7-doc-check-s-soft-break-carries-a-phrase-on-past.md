---
id: PL-Z1R7
title: doc_check's SOFT_BREAK carries a phrase on past the line where a paragraph or heading ends - an ATX heading's own line, or a paragraph that a block quote, a setext underline or a table with no outer pipe opening under it ends - so every GAP and QUOTATION_CHAR reader reads past the statement: a § quotation its paragraph never closes reads as closed, a setext variant cites a section nobody wrote, and mentions and a citation's above or below join a heading to the paragraph under it; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tools/possessive_section_check.py, subprojects/docket/src/docket/roadmap.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
closed: 2026-10-10
pr: 1388
payoff: a quotation, a link text or a mention is read inside the paragraph or heading that holds it, so a block quote, setext underline, table or heading under it ends the statement where GitHub ends it
verify: grep -qF '"soft break, a block quote' tests/unit/test_doc_check.py && grep -qF '"soft break, a setext' tests/unit/test_doc_check.py && grep -qF '"soft break, a table' tests/unit/test_doc_check.py && grep -qF '"soft break, an ATX heading' tests/unit/test_doc_check.py
---

**Problem.** doc_check's SOFT_BREAK carries a phrase on past the line where a paragraph or heading ends - an ATX heading's own line, or a paragraph that a block quote, a setext underline or a table with no outer pipe opening under it ends - so every GAP and QUOTATION_CHAR reader reads past the statement: a § quotation its paragraph never closes reads as closed, a setext variant cites a section nobody wrote, and mentions and a citation's above or below join a heading to the paragraph under it; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), by the auditors
of both halves of `tools/doc_check.py` and of `docket.roadmap`. `SOFT_BREAK`
takes a line ending for a soft break wherever the next line passes
`docket.roadmap.CONTINUED_LINE`, its only consumer, and asks nothing about where
the break stands; `CONTINUED_LINE` takes any run of `>` for a container prefix,
so a block quote opening under a paragraph, a nested one opening inside a
quote, and one opening inside a list item all read as the paragraph going on. CommonMark 0.31.2 ends a paragraph at a block
quote opening under it (§ 5.1) and at a setext underline of `=` or of one or two
`-` (§ 4.3), GFM 0.29 at a table whose header row has no outer pipe (§ 4.10),
and an ATX heading, a thematic break and a one-line HTML block end on their own
line (§ 4.2, § 4.1, § 4.6), so no soft break follows any of them. `GAP`,
`STATEMENT_RE`, `QUOTATION_CHAR` and every pattern built on them read on.
`PL-2S1G`, a member, set out to refuse only what CommonMark lets interrupt a
paragraph and checked the early-end direction; these are the late one.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0 (`docket.markdown.statement_lines` agrees with it
on every input). Each pair of lines below is one statement to `STATEMENT_RE`
and two to the reference:

```text
Foo
> bar

Foo
=
Bar

Foo
Bar | Baz
--- | ---
x | y

## Dosing
limits are read from the agent's data file.
```

What it changes: a paragraph opening a section-mark quotation of `Foo` that the
block quote under it closes (`bar"` on the quoted line) passes
`check_citations`, where markdown-it reads the quotation as unclosed and
`doc_check`'s own refusal fires once a blank line separates the two; the setext
form reports a cited section named `Foo = bar` instead of that refusal;
`QUOTED_SOURCE_RE`, `ITEM_SECTION_RE`, `UNMARKED_CITATION_RE`,
`possessive_section_check.POSSESSIVE_RE` and `LINK_RE` each read a quotation or a
link text across a quoted line's `>`; `mentions` finds `Dosing limits` on the
heading's line; and a heading quoting a section, over a paragraph opening with
`above`, reads as citing it above. Latent: of 2,601 block ends sitting directly
over a non-blank line in the 2,465 tracked Markdown files, and seven read-past
points the auditor of the first half counted, none changes an answer.

**Why it matters.** Every `GAP` and `QUOTATION_CHAR` reader in `doc_check` holds a cited section, a quotation, a link or a mention to the tree, so a statement read past its end checks words its writer never put together: a quotation its paragraph never closes passes, a setext variant cites a section nobody wrote, and a heading is joined to the paragraph under it.

**Generator check.** A member of `PL-R417`: one shared pattern carries a
statement on past the line its format ends it at. `PL-BYJ5` and `PL-T73L` were
the same readers crossing a blank line.

**Done when.** Each `GAP` and `QUOTATION_CHAR` reader matches within one
statement of `docket.markdown.statement_lines`, as `_statement_spans` already
reads code spans, rather than deciding a statement's end by `CONTINUED_LINE`'s
test of the next line alone, pinned by a `soft break, ` case in `PL-R417`'s
guard for each form above, failing on today's reader.

**Built 2026-10-10 (`#1388`).** `doc_check._statement_matches` runs a pattern
over one `statement_lines` statement at a time, bounded to it, and every `GAP`
and `QUOTATION_CHAR` reader now matches through it: `_withheld_counts`,
`declares_none`, `_version_claim`, both citation patterns and
`_cited_section`'s direction, `check_quoted_sources`, `mentions`, and
`tools/possessive_section_check.py`. A match carries its statement's bounds, so
a look-behind window or a match read on from it stops at the statement's end
too. Five `soft break, ` cases, each failing on main's readers; `python3
tools/doc_check.py check` and `tools/possessive_section_check.py` report the
same over the tree before and after.
