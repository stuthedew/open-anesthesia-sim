---
id: PL-TH9V
title: Inline math in docs/MODEL.md renders as literal parentheses on GitHub
priority: P2
effort: S
status: done
classes: defect, docs
touches: docs/MODEL.md, docs/WORKING_NOTES.md, docs/items, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-01
closed: 2026-09-01
pr: 136
verify: python3 tools/doc_check.py check && uv run pytest tests/unit/test_doc_check.py -k math
---

**Problem.** Markdown across the repository wrote inline math with LaTeX's
`` `\(...\)` `` delimiters, which GitHub does not recognise. `(` and `)` are
ASCII punctuation, so CommonMark consumes the backslash as an ordinary
character escape before any math parser runs: `` `\(t\)` `` reached the page as
the literal text `(t)`, and `` `\(\Delta t\)` `` as `(\Delta t)` — the `\D`
surviving only because `D` is not escapable. The symbol table in
`docs/MODEL.md` was the most visible casualty; every row of it was affected.

**Why it mattered.** `docs/MODEL.md` is the authoritative specification for the
implemented model, and its symbol table is the key a reader uses to map a
displayed clinical value back to the equation and units that produced it. A key
whose left-hand column does not render is a traceability failure rather than a
cosmetic one: `\lambda_{b:g}` shown raw does not tell a reader it is the
blood:gas partition coefficient, and the rows that did render — `(F_a)` and
`(F_A)` — differed only in a subscript's case, which is exactly the distinction
the missing formatting was carrying.

**Scope, as found.** 111 broken spans across 9 files: 98 in `docs/MODEL.md`, 1
in `docs/WORKING_NOTES.md`, and 12 across seven queue items that had copied the
form out of `docs/MODEL.md` (`PL-004`, `PL-042`, `PL-0MLQ`, `PL-629Z`,
`PL-6GS0`, `PL-VP7N`, `PL-Y5BV`). No occurrence anywhere sat inside a code
fence or code span, so the conversion could not corrupt a code sample.

**A second, independent failure.** Four expressions were split across a source
line break by paragraph reflow — `docs/MODEL.md` lines 632, 645 and 1327, and
`PL-VP7N` line 109. Inline math is parsed within a line, so a split expression
renders as literal text on both sides. The one at line 1327 was already on the
correct `$...$` delimiters and broken only by the wrap, which is why this half
of the defect outlives the conversion and needed a check of its own.

**Approach — verified against GitHub's "Writing mathematical expressions",
2026-09-01.** GitHub renders LaTeX through MathJax and documents exactly two
inline delimiters, `$...$` and `` $`...`$ ``, the latter "useful when the
expression you are writing contains characters that overlap with markdown
syntax". `` `\(...\)` `` appears nowhere on the page.

The conversion targeted `` $`...`$ `` rather than bare `$...$`. The `F_a`
symbol-table row carries two expressions on one line, so under bare `$` it
would hold four delimiters and three `_` characters, with the text between the
middle pair sitting exactly where markdown reads emphasis — the overlap case
the documentation names the backtick form for. The choice also happens to be
length-neutral (`` `\(x\)` `` and `` $`x`$ `` are both five characters), so no
paragraph needed rewrapping beyond the four repairs above.

**Ten display blocks were splitting a sentence.** Because inline math did not
work, single symbols had been set as `$$` blocks mid-sentence — "Let:", then
`M_x` centred on its own line, then "denote the equivalent gas volume …". Those
are collapsed back inline. The rule applied, and worth keeping: **collapse a
block when the prose after it continues the same sentence; leave it when the
sentence ends at the block**, which is ordinary mathematical typesetting and
reads correctly. 46 display blocks remain on that rule, down from 58.

**Made decidable.** `check_math_delimiters` in `tools/doc_check.py` refuses any
markdown file carrying `` `\(` ``, `` `\)` ``, `` `\[` `` or `` `\]` `` outside
code, and refuses an unpaired `` `$` ``-backtick edge, which is what a
line-split expression leaves behind. It reads every markdown file rather than
`DOC_GLOBS`, because rendering is not a claim held to the tree and a queue item
renders on GitHub like anything else. Code fences, code spans and well-formed
math spans are blanked before either rule runs, so a quotation of the broken
syntax — this item is full of them — is not a use of it.

**Not done here.** The 46 surviving `$$` blocks are correct as written and were
left alone. GitHub also accepts a ```` ```math ```` fence as an equivalent.
Both forms put their delimiters on their own lines, so neither is exposed to
the wrap defect the way an inline span is, and there is no case for converting
the existing blocks — the fence is worth knowing about, not worth a pass.

**Verified.** `python3 tools/doc_check.py check` is clean across all 227 tracked
markdown files with no false positives; `make check` passes. Rendering itself is
not machine-checkable from a session — it was confirmed by eye on the pushed
branch.
