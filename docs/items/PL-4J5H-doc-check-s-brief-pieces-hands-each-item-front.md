---
id: PL-4J5H
title: doc_check's _brief_pieces hands each item front-matter field to Markdown readers whole, so a field that docket.model's fold and YAML read as one value is cut where Markdown would end a paragraph - an interior blank or comment line, or a continuation line opening a list item, a block quote, a fence, an HTML tag or a thematic break - and a quotation, citation or code span carried across the cut goes unread or is refused as unclosed; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, subprojects/docket/src/docket/model.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1431
payoff: a front-matter field's quotation, citation or code span is checked as the one value docket reads, not refused or missed at a Markdown paragraph cut
verify: grep -q 'def test_a_front_matter_field_reaches_the_markdown_readers_as_one_statement' tests/unit/test_doc_check.py
---

**Problem.** doc_check's _brief_pieces hands each item front-matter field to Markdown readers whole, so a field that docket.model's fold and YAML read as one value is cut where Markdown would end a paragraph - an interior blank or comment line, or a continuation line opening a list item, a block quote, a fence, an HTML tag or a thematic break - and a quotation, citation or code span carried across the cut goes unread or is refused as unclosed; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditors of
`docket.model`/`docket.frontmatter` and of both
halves of `tools/doc_check.py`. `_brief_pieces` gives each front-matter field
its span from `docket.model.front_matter_spans` and its callers
(`check_quoted_sources` through `_quoting_sources`, `_check_brief_paths`,
`check_line_citations`, and `possessive_section_check.sites`) read each piece
as Markdown. `docket.model._fold` folds every indented line under a field into
its value with one space, across an interior blank or `#` line too, and its
docstring says an indented `- ...` under a prose field is prose; YAML 1.2.2
folds a plain scalar the same way (§ 7.3.3). CommonMark 0.31.2 ends the piece's
paragraph at a blank line (§ 4.8) and lets a list item, block quote, fence,
HTML block or thematic break interrupt it (§ 5.2, § 5.1, § 4.5, § 4.6, § 4.1).
`front_matter_spans`' docstring says a blank or comment line is in no span,
which is false for an interior one.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against `docket.model`, PyYAML 6.0.3 and ruamel.yaml 0.19.1, which
each read the field as one string with the quotation closed:

```text
reason: the rule `CLAUDE.md`'s "Capture, always, and capture cheaply. Any defect
  - or idea identified in a session" is the one this follows
reason: see `docs/target.md`'s "Alpha

  beta gamma" here
```

The first is refused as a quotation its paragraph never closes; the second,
and the same field with a comment line in place of the blank, gives no match.

Latent: 13 fields across all items continue onto another line, and none is
split by a Markdown block start or holds an interior blank or comment line.

**Re-confirmed 2026-10-11** on main at `16a20a4f`: `docket.model` reads each form
above as one value with its quotation closed, and `_brief_pieces` hands
`QUOTED_SOURCE_RE` a piece in which all three, the list-item line, the blank
line and a comment line in its place, match as a quotation left `unclosed` at
the cut. Still 13 continued fields across the store, none of these shapes.

**Why it matters.** The quoted-source and citation checks are what hold a
brief's quotation to its source. Read at a Markdown cut, a correct quotation
is refused as unclosed or a stale one goes unchecked, so the check's answer on
such a field means nothing.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1389`: the gap closed `PL-CZ28`'s fix left. Latent, so an ordinary item under that head's `spent` verdict: found live in a tracked file, it reopens `PL-R417` (2026-10-11 triage).

**Done when.** Each field reaches the Markdown readers as `_fold` reads it -
one statement, its continuation lines joined - or is declined by name, with a
test per form above; `front_matter_spans`' docstring says what it returns for
an interior line.

**Done 2026-10-12** (`#1431`). `docket.model.front_matter_spans` returns each
field as a `FieldSpan`: its key, its span, and the interior lines `_fold` reads
past, which its docstring now says lie in the field's span. `_brief_pieces`
hands each field over as `_fold` reads it, one statement: each line folded into
it is indented four columns more, past where any block can open, so a list
item, a fence, an HTML tag or a thematic break no longer ends the paragraph. Two
forms are declined by name in the run's "Not checked" list, with the field's
line and a fix: an interior blank, comment or unread line, which no Markdown
paragraph crosses, and a continuation line opening with `>`, which `SOFT_BREAK`
drops as a block quote's marker where `_fold` reads it as text.
`possessive_section_check.sites` reads the same pieces through
`_quoting_sources`. Pinned by
`test_a_front_matter_field_reaches_the_markdown_readers_as_one_statement` in
`tests/unit/test_doc_check.py`, seven forms, each refused on `main` as a
quotation its paragraph never closes. Over today's store no field is declined
and no finding changed.
