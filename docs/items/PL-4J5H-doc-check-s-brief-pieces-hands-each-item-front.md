---
id: PL-4J5H
title: doc_check's _brief_pieces hands each item front-matter field to Markdown readers whole, so a field that docket.model's fold and YAML read as one value is cut where Markdown would end a paragraph - an interior blank or comment line, or a continuation line opening a list item, a block quote, a fence, an HTML tag or a thematic break - and a quotation, citation or code span carried across the cut goes unread or is refused as unclosed; latent
status: untriaged
feature: one-answer
added: 2026-10-10
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

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1389`: the gap closed `PL-CZ28`'s fix left.

**Done when.** Each field reaches the Markdown readers as `_fold` reads it -
one statement, its continuation lines joined - or is declined by name, with a
test per form above; `front_matter_spans`' docstring says what it returns for
an interior line.
