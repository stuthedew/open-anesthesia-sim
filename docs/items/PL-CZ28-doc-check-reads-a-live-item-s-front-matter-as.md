---
id: PL-CZ28
title: doc_check reads a live item's front matter as one Markdown paragraph in _check_brief_paths, check_quoted_sources and check_line_citations, so a backtick or a quotation one field leaves open pairs with the next field's, hiding a deleted path a later field cites or quoting a source across two fields; latent
status: untriaged
feature: one-answer
added: 2026-10-06
---

**Problem.** doc_check reads a live item's front matter as one Markdown paragraph in _check_brief_paths, check_quoted_sources and check_line_citations, so a backtick or a quotation one field leaves open pairs with the next field's, hiding a deleted path a later field cites or quoting a source across two fields; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing the
second half of `tools/doc_check.py`. A docket front-matter field is `key:
value` and the indented lines `docket.model._fold` folds into it, and it ends at
the next key. `_check_brief_paths` reads the whole file through
`_statement_spans`, `check_quoted_sources` through `_quoting_sources`, and
`check_line_citations` likewise, so the front matter is one paragraph to them,
and a code span (CommonMark 0.31.2 § 6.1) or a quotation opened in one field
runs into the next.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against `docket.model.parse_front_matter`. An item whose `title:` says the
reader counts a stray backtick, written with one, and whose later `payoff:`
cites a path git history shows deleted:

```text
title: The reader counts a stray ` backtick
payoff: no brief cites `tools/gone.py` once it is gone
```

`_check_brief_paths` reported nothing; with the stray backtick removed from the
title it reported the deleted path on the `payoff:` line. `parse_front_matter`
reads the two fields apart, and the payoff alone holds the code span
`tools/gone.py`. A second item, whose `title:` ends inside an opened quotation
after a section mark and whose `summary:` closes it, made
`check_quoted_sources` read one quotation spanning the `priority:` field
between them; `parse_front_matter` keeps the fields apart. Latent: over the 310
live briefs, no match crosses a field's end.

**Generator check.** A member of `PL-R417`: three readers take the front
matter's fields for one statement, where each ends at the next key.
`doc_check` already reads where a front matter ends, in `_frontmatter_end`
(since `#506`), and `check_math_delimiters` starts past it; these three readers
start at line 1.

**Done when.** The three readers read each front-matter field on its own,
through `parse_front_matter`, and the brief from `_frontmatter_end` on, pinned
by a `brief paths, ` and a `quoted sources, ` case in `PL-R417`'s guard that
fail on today's reader.
