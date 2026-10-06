---
id: PL-B83V
title: docket.markdown reads a closing pre, script, style or textarea tag alone on its line as a paragraph, where CommonMark 0.31.2 excludes those names only from an open tag and opens an HTML block running to the next blank line, so a heading, block quote, list item or fence under it is read as a block of its own by every reader of the one Markdown reader; latent
status: untriaged
feature: one-answer
added: 2026-10-06
---

**Problem.** docket.markdown reads a closing pre, script, style or textarea tag alone on its line as a paragraph, where CommonMark 0.31.2 excludes those names only from an open tag and opens an HTML block running to the next blank line, so a heading, block quote, list item or fence under it is read as a block of its own by every reader of the one Markdown reader; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`docket.markdown`, the shared reader. CommonMark 0.31.2 § 4.6 opens an HTML
block of the seventh kind at a line holding only a complete open tag, with any
tag name other than `pre`, `script`, `style` or `textarea`, or a complete
closing tag, and the block runs on to a blank line. The exclusion binds the open
tag alone, in the 0.31.2 text as in 0.29 and 0.30. `_HTML_TAG_LINE` applies it
to the closing tag too, so `_parse`, and through it `read`, `statement_lines`,
`headings`, `tables`, the fences reader and the roadmap walker, take a lone
closing tag of those four names for a paragraph and read the line under it
afresh.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0 and commonmark.py 0.9.1:

```text
</pre>
# Not a heading
```

`docket.markdown` read a paragraph and then a heading, and `headings` gave `Not
a heading`; markdown-it read one HTML block over both lines and commonmark.py
rendered both as raw HTML. A closing `script` tag over a block quote line, a
closing `style` tag over a list item and a closing `textarea` tag over a fence
read the same way, as a quote, an entry and a fence. The controls, a closing
`div` or `span` tag over a heading, agree in all three readers. Latent: no
tracked Markdown file holds a closing tag of those four names at all.

**Generator check.** A member of `PL-R417`: the one reader of where a Markdown
block ends takes a line for a block of its own where the format carries an HTML
block over it. Over the specification's 652 examples, `docket.markdown` departs
from markdown-it only where it declares a departure; this is the one form the
auditor's fuzzing found outside those.

**Done when.** `_HTML_TAG_LINE`'s closing-tag branch admits every tag name, as
the specification's seventh condition does, pinned by a `markdown blocks, ` case
in `PL-R417`'s guard for each of the four names, failing on today's reader.
