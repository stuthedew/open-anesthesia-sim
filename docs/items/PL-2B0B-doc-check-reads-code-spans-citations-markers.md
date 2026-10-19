---
id: PL-2B0B
title: doc_check reads code spans, citations, markers and TeX inside indented code blocks and HTML blocks - _statement_spans and _code_spans call statement_lines with no kinds, _statement_matches without kinds reads citations and the Tags claims in comments, _absent_paths takes a marker inside indented code, _without_code checks TeX inside a comment, and LINE_CITATION_RE ignores both - so a test name, path or claim on no rendered page is checked; latent
priority: P3
effort: M
status: done
classes: defect
milestone: v0.5.34
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-10
closed: 2026-10-19
pr: 1631
payoff: a marker, a line citation, a TeX delimiter or a claim written inside an indented code block or an HTML comment no longer fails make check for a page nobody renders
verify: grep -q 'def test_a_marker_in_an_indented_code_block_marks_nothing' tests/unit/test_doc_check.py && grep -q 'def test_a_line_citation_in_an_indented_code_block_or_a_comment_is_not_held' tests/unit/test_doc_check.py && grep -q 'def test_tex_in_an_html_block_is_quiet' tests/unit/test_doc_check.py && grep -q 'def test_a_claim_in_an_indented_code_block_or_a_comment_is_not_read' tests/unit/test_doc_check.py
---

**Problem.** doc_check reads code spans, citations, markers and TeX inside indented code blocks and HTML blocks - _statement_spans and _code_spans call statement_lines with no kinds, _statement_matches without kinds reads citations and the Tags claims in comments, _absent_paths takes a marker inside indented code, _without_code checks TeX inside a comment, and LINE_CITATION_RE ignores both - so a test name, path or claim on no rendered page is checked; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditors of
all three parts of `tools/doc_check.py`. An
indented code block's content is literal (CommonMark 0.31.2 § 4.4) and an HTML
comment is not rendered (§ 4.6), so neither holds a code span, citation or
marker a reader sees.

```text
    see `test_ghost_one` here

<!--
see `test_ghost_two` and `docs/gone.md`
-->
```

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against cmark-gfm 0.29, which renders the first as a code block and
omits the comment: `_named_tests` returns both test names, so
`check_named_tests` would report them; the comment's path is checked as a
citation. `_undated_host_claims` reads no `<details>` block GitHub does
render, the other direction. Latent: none in the documents today.

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`: `_named_tests` returns
both test names, and `check_citations` refuses `docs/gone.md` in the indented
block and in the comment - and in a fenced copy too, which `_code_spans` reads
on purpose so a package map's comments are held to the tree.
`_statement_spans`' docstring states the same choice for an indented code
block and an HTML block, read "as a fence's lines are", so the span half of
this item reverses a documented design rather than repairing an oversight.

**Generator check.** Not a member of `PL-R417`: the wrong kind of block, read
at the right extent. `PL-KR6M`, untriaged, names three section-mark readers
that read an indented code block as prose; this is the same fault in the span,
citation, marker and TeX readers.

**Narrowed 2026-10-12 by `PL-KR6M`**, recorded at its triage as the `spent`
head this item is a member of. `#1434` moves `check_citations`' two
section-mark readers onto `markdown.PROSE`, so a section cited in an indented
code block or an HTML comment is no longer held. The rest stands: the span,
path-citation, marker, TeX, named-test and `Tags` readers, and the design half
above.

**Why it matters.** A check reading a block no page renders fails a document
for a test name or path no reader sees, or holds it to a claim nobody makes.
Latent: no document holds one today, so the cost falls on the next session that
writes an example in an indented block and is refused by `make check`.

**Done when.** Each of the four readers the decision below names reads what
`markdown.PROSE` reads: a marker inside an indented code block, and a line
citation, a TeX delimiter and a claim sentence inside an indented code block
or an HTML comment, are read by none of them, where a fenced copy already is
not, pinned by the four tests the `verify:` names; and the span and
path-citation readers are unchanged.

**Decision needed.** Whether the span and citation readers keep the documented
choice to read an indented code block and an HTML block as a fence's lines are,
which this item would reverse. **Recommendation: keep it, and narrow this item
to the marker, TeX and `Tags` readers**, whose docstrings state no such choice.
A path or test named in any block is held to the tree on purpose, so that a
package map's comments stay true, and that design errs strict rather than
wrong. If those readers, once read, state the same choice, drop the item with
that as its reason.

**Decided 2026-10-12, in the second workflow decision batch: the span and
path-citation readers keep their choice, and this item narrows to the four
readers that state none.** Read against `main` at `43d5aeaa`.
`_statement_spans`' docstring reads an indented code block's and an HTML
block's spans "as a fence's lines are", and `_code_spans` reads a fence's
lines so a package map's comments in `docs/ARCHITECTURE.md` and
`docs/apparatus.md` are held to the tree (`PL-9L39`, `PL-R417`); so
`check_citations`' path half, `_check_brief_paths` and `_named_tests` hold a
path or a test named in any block on purpose, strict rather than wrong, and
reversing it would reopen `PL-R417`'s reading. The four below state the
opposite reason for a fence and none for the other two blocks, which is the
oversight `PL-KR6M` fixed in its three readers, so the fix is the same one:

- `_absent_paths`, whose docstring says "A marker shown in a fence is the
  format being shown, and is not read", reads a marker inside an indented
  code block;
- `check_line_citations`, whose comment says "A fence holds a literal", reads
  a line citation inside an indented code block and an HTML comment;
- `_without_code`, "so only prose reaches the math rules", blanks fences and
  indented code and leaves an HTML block to the math rules;
- the claim readers that pass `statement_lines` no kinds: `_tags_region` and
  `_version_claim` for the `Tags` claims, `check_quoted_sources` through
  `QUOTED_SOURCE_RE` and `ITEM_SECTION_RE`, `_withheld_counts` through
  `NOT_DELEGABLE_COUNT_RE`, and `check_bound_families`' `declares_none`. The
  section citations pass `markdown.PROSE` since `#1434`.

Which block is prose is `markdown.PROSE`'s one record, so each reader takes
its answer from there rather than from a list of its own. The other direction,
a `details` or `div` block GitHub renders whose lines `markdown.PROSE` holds
literal, named in the reproduction above, is `PL-PSQN`'s, filed by this batch.
A reader's own stated choice settles which side it is on, so this was decided
in the round under rule 14 of `.claude/rules/instruction-writing.md` and not
offered; the Done-when above is rewritten to the four.

**Closed 2026-10-19.** `check_line_citations`, `check_math_delimiters`, and
the claim readers (`_withheld_counts`, `_version_claim`, `check_bound_families`'
`declares_none`, and `check_quoted_sources` for a Markdown source) now read
only the blocks `markdown.PROSE` names. A docstring source keeps the whole
read, because its lines after the first are indented and Markdown would read a
later paragraph as code. On the tree the change dropped none of the 78 line
citations or the 551 quotation matches read before it. `_absent_paths` needed
no change: `PL-7454` (#1444) had already made `_marker_lines` read a marker
only where it opens an HTML block, so the marker test pins that reading. The
span and path-citation readers are unchanged, as decided on 2026-10-12.
