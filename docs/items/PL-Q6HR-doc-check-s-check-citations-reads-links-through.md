---
id: PL-Q6HR
title: doc_check's check_citations reads links through _statement_matches over _without_spans' blanked text, so statement_lines re-reads a document whose code spans are now spaces: a wrapped line holding only a code span becomes a blank line that ends the paragraph, and a paragraph opening with one becomes an indented code block that is skipped, and a link around or after either is never read; live in form
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** doc_check's check_citations reads links through _statement_matches over _without_spans' blanked text, so statement_lines re-reads a document whose code spans are now spaces: a wrapped line holding only a code span becomes a blank line that ends the paragraph, and a paragraph opening with one becomes an indented code block that is skipped, and a link around or after either is never read; live in form

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`tools/doc_check.py`'s middle part.
`check_citations` runs `_statement_matches(LINK_RE, _without_spans(text),
PROSE)`, so the statements are read from the blanked text rather than from the
document. Blanking a code span to spaces changes what CommonMark 0.31.2 sees: a
line holding only the span becomes blank and ends the paragraph (§ 4.8), and a
paragraph that opens with a span opens with four or more spaces, which is an
indented code block (§ 4.4) and not `PROSE`.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against markdown-it-py 4.2.0 and cmark-gfm 0.29, which read each as
one paragraph holding the link:

```text
See [the notes of
`docket check`
for the rule](missing-file.md) here.

`docs/MODEL.md` is the spec; see [the notes](missing-file.md).
```

In the first, the statements go from one to two and `LINK_RE` reads nothing;
with the backticks removed, `check_citations` reports the missing target. In
the second the block reads as code and the link error disappears.

Live in form: in 31 documents the prose statements are cut differently once
spans are blanked (`ROADMAP.md`, `CLAUDE.md` and `docs/MODEL.md` among them);
read with the original text's statement bounds, no link reading differs today.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1388` (`PL-M2J4`'s fix).

**Done when.** `check_citations` takes its statements from the document and
only its matching from the blanked text, so both forms above report the
missing target; each is a `CONTINUED_STATEMENTS` case.
