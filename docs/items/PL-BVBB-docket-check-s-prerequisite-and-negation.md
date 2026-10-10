---
id: PL-BVBB
title: docket check's prerequisite and negation windows are measured in characters of _unmarked text, which keeps a continuation line's indentation and its blanked container markers, so a waits-on clause wrapped before its id is missed in a third-level list item and a negation wrapped across an indented line is missed; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** docket check's prerequisite and negation windows are measured in characters of _unmarked text, which keeps a continuation line's indentation and its blanked container markers, so a waits-on clause wrapped before its id is missed in a third-level list item and a negation wrapped across an indented line is missed; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.checks`. `_prerequisite_matches` runs
`_cue_pattern` (a gap of at most 40 characters between a cue and its id) and
`NEGATED_CUE` (a 24-character look-back) over `_unmarked`, which blanks a
continuation line's container markers to spaces and keeps its indentation.
CommonMark 0.31.2 strips a paragraph continuation line's leading whitespace
(§ 4.8) and reads the line ending as one soft break (§ 6.8), so the statement's
text holds one break where the window counts every column of the indent.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against markdown-it-py 4.2.0, whose inline content for each case is
the same text with one line break:

```text
It waits on the outcome of the design round in
`PL-ZZZZ`.

      - It waits on the outcome of the design round in
        `PL-ZZZZ`.

This item is not
                         blocked by `PL-ZZZZ`.
```

The first is read as a prerequisite at the top level and inside a list item,
and not inside a third-level list item, where the continuation's indent fills
the window; the third reads as a prerequisite, where the same sentence on one
line reads as negated. Latent: over 2,124 items, no paragraph continuation
line's unmarked leading whitespace exceeds seven columns, and no answer
differs.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-WF35`'s and `PL-YCJJ`'s fixes left: a
waits-on clause wrapped before its id is still unread where the wrap is
indented.

**Done when.** Each window is measured over the statement's text with every
soft break and the whitespace around it read as one space, and each form above
is a test in docket's checks tests.
