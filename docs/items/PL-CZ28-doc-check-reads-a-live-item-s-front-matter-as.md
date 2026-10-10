---
id: PL-CZ28
title: doc_check reads a live item's front matter as one Markdown paragraph in _check_brief_paths, check_quoted_sources and check_line_citations, so a backtick or a quotation one field leaves open pairs with the next field's, hiding a deleted path a later field cites or quoting a source across two fields; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, subprojects/docket/src/docket/model.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
closed: 2026-10-10
pr: 1389
payoff: a live brief's front-matter fields are each read on their own, so a stray backtick or quotation in one field cannot hide a deleted path a later field cites or join two fields into one quotation
verify: grep -qF '"brief paths, a stray backtick in one front-matter field' tests/unit/test_doc_check.py && grep -qF '"quoted sources, a quotation one front-matter field leaves open' tests/unit/test_doc_check.py
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

**Why it matters.** These three checks hold a live brief's cited paths,
quotations and line citations to the tree, and a brief's front matter is where
its title, payoff and `verify:` command cite paths. A backtick or quotation
one field leaves open pairs with the next field's, so a deleted path a later
field cites is never reported, or a quotation is checked as words spanning two
fields that no source holds.

**Generator check.** A member of `PL-R417`: three readers take the front
matter's fields for one statement, where each ends at the next key.
`doc_check` already reads where a front matter ends, in `_frontmatter_end`
(since `#506`), and `check_math_delimiters` starts past it; these three readers
start at line 1.

**Done when.** The three readers read each front-matter field on its own,
through `parse_front_matter`, and the brief from `_frontmatter_end` on, pinned
by a `brief paths, ` and a `quoted sources, ` case in `PL-R417`'s guard that
fail on today's reader.

**Built 2026-10-10 (`#1389`).** `docket.model.front_matter_spans` gives the
lines each front-matter field takes, as `_fold` reads them for
`parse_front_matter`, and where the body starts: the readers need each field's
lines rather than its folded value, to name the line a match is on.
`doc_check._brief_pieces` cuts a live brief into those pieces - each field,
every other front-matter line alone, and the body - and `_check_brief_paths`,
`check_line_citations` and `_quoting_sources` read a brief a piece at a time,
each match's line counted from its piece's first. `possessive_section_check`
takes `_quoting_sources`, so it reads the same way. A `brief paths, ` and a
`quoted sources, ` case in the guard, each failing on main's readers;
`doc_check` and `possessive_section_check` report the same over the tree before
and after.
