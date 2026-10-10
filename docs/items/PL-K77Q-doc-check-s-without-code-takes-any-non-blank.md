---
id: PL-K77Q
title: doc_check's _without_code takes any non-blank line for an open paragraph, so an indented code block directly under an ATX heading, a thematic break or a one-line HTML comment is read as that paragraph's continuation and TeX-shaped text in it is refused as math GitHub does not render; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
closed: 2026-10-10
pr: 1388
payoff: an indented code block under a heading, a thematic break or a one-line comment is read as code, so TeX-shaped text in it is never refused as math
verify: grep -qF '"math, ' tests/unit/test_doc_check.py
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

**Why it matters.** `check_math_delimiters` refuses TeX-shaped text GitHub does not render as math, so an indented code block read as prose is refused for a literal a reader sees as code.

**Generator check.** A member of `PL-R417`: a reader carries a paragraph on
past a block that ends on its own line. `PL-Z8RS` and `PL-FP7J`, both members,
fixed this function's code spans and its blank-line end, not this form.

**Done when.** `_without_code` takes code blocks from `docket.markdown`'s
`block_lines` with `CODE` rather than its own paragraph flag, pinned by a
`math, ` case in `PL-R417`'s guard for each of the three forms, failing on
today's reader.

**Built 2026-10-10 (`#1388`).** `_without_code` blanks the lines `block_lines`
reads as an indented code block, beside the fenced ones, rather than keeping a
paragraph flag of its own, so a block indented four columns directly under an
ATX heading, a thematic break or a one-line HTML comment is code to it, as
CommonMark reads it. `LIST_ITEM_RE` and `_content_column`, which only that flag
read, went with it. Three `math, ` cases, each failing on main's reader;
`python3 tools/doc_check.py check` reports the same over the tree before and
after.
