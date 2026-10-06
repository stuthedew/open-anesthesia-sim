---
id: PL-K77Q
title: doc_check's _without_code takes any non-blank line for an open paragraph, so an indented code block directly under an ATX heading, a thematic break or a one-line HTML comment is read as that paragraph's continuation and TeX-shaped text in it is refused as math GitHub does not render; latent
status: untriaged
feature: one-answer
added: 2026-10-06
---

**Problem.** doc_check's _without_code takes any non-blank line for an open paragraph, so an indented code block directly under an ATX heading, a thematic break or a one-line HTML comment is read as that paragraph's continuation and TeX-shaped text in it is refused as math GitHub does not render; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing the
second half of `tools/doc_check.py`. `_without_code` blanks literal text before
`check_math_delimiters` reads a document, and blanks an indented line only where
no paragraph is open, since an indented code block cannot interrupt one
(CommonMark 0.31.2 § 4.4). Its paragraph flag is set by any non-blank line. But
an ATX heading (§ 4.2), a thematic break (§ 4.1) and a one-line HTML block
(§ 4.6) each end on their own line, so a line indented four columns directly
under one opens a code block.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0. A heading, then an indented line holding a
TeX-shaped group, and the same line under a thematic break and under a one-line
HTML comment:

```text
## Heading
    \(\d+\)
```

`_without_code` left the line unblanked and `check_math_delimiters` gave two
errors in each case; markdown-it reads the line as a code block in all three,
and `docket.markdown.block_lines` with `CODE` agrees. Under a paragraph line the
indented line is a lazy continuation, which both read alike. Latent: no line of
the 2,465 tracked Markdown files reads differently in either direction.

**Generator check.** A member of `PL-R417`: a reader carries a paragraph on
past a block that ends on its own line. `PL-Z8RS` and `PL-FP7J`, both members,
fixed this function's code spans and its blank-line end, not this form.

**Done when.** `_without_code` takes code blocks from `docket.markdown`'s
`block_lines` with `CODE` rather than its own paragraph flag, pinned by a
`math, ` case in `PL-R417`'s guard for each of the three forms, failing on
today's reader.
