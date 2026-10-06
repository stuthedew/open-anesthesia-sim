---
id: PL-CQC9
title: docket.release's markdown_title takes a backslash-escaped backtick for a code span's opener, so in a title holding one before a placeholder in angle brackets the placeholder is copied unescaped into the notes bullet or capture line, where GitHub drops it as an HTML tag; latent
status: untriaged
added: 2026-10-06
---

**Problem.** docket.release's markdown_title takes a backslash-escaped backtick for a code span's opener, so in a title holding one before a placeholder in angle brackets the placeholder is copied unescaped into the notes bullet or capture line, where GitHub drops it as an HTML tag; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`docket.release`. `markdown_title` escapes each `<` outside a code span, so a
placeholder such as `refs/pull/<n>/head` survives in the rendered notes
(`PL-PRSF`), and copies a code span as it stands. `CODE_SPAN_RE` finds the
spans, and it does not ask whether a backtick is backslash-escaped. In
CommonMark 0.31.2 an escaped backtick is a literal character and opens no code
span (§ 2.4, whose example reads it as not code).

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0, with a title holding an escaped backtick, then
`refs/pull/<n>/head`, then a code span: `markdown_title` returned it
unchanged, the `<` not escaped, because the span it found ran from the escaped
backtick to the code span's opener. markdown-it rendered that output with `<n>`
as raw HTML, and the escaped form as the text `<n>`. Latent: no tracked title
holds an escaped backtick.

**Generator check.** Not a member of `PL-R417`: a title is one line, and the
misread is inside it.

**Done when.** `markdown_title` reads code spans as CommonMark does, an escaped
backtick opening none, pinned by a test with the title above.
