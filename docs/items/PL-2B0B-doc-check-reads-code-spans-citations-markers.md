---
id: PL-2B0B
title: doc_check reads code spans, citations, markers and TeX inside indented code blocks and HTML blocks - _statement_spans and _code_spans call statement_lines with no kinds, _statement_matches without kinds reads citations and the Tags claims in comments, _absent_paths takes a marker inside indented code, _without_code checks TeX inside a comment, and LINE_CITATION_RE ignores both - so a test name, path or claim on no rendered page is checked; latent
status: untriaged
added: 2026-10-10
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

**Done when.** Each reader passes the kinds it reads to `statement_lines` (or
blanks fences, indented code and HTML blocks first), so the forms above are
read as GitHub renders them; a test pins each.
