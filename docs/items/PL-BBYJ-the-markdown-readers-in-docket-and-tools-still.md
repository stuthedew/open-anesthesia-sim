---
id: PL-BBYJ
title: The Markdown readers in docket and tools still split with str.splitlines(), which breaks at U+2028, U+0085 and form feed where CommonMark ends no line, and pair their line indices with fences.py's; tests/unit/test_line_splits.py exempts their files until they convert together
status: untriaged
feature: line-ends
touches: subprojects/docket/src/docket/fences.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/instructions.py, subprojects/docket/src/docket/notes.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/lines.py, tools/doc_check.py, tools/core_vocabulary_check.py, tools/dead_ends.py, tests/unit/test_line_splits.py
added: 2026-10-05
---

**Problem.** The Markdown readers in docket and tools still split with str.splitlines(), which breaks at U+2028, U+0085 and form feed where CommonMark ends no line, and pair their line indices with fences.py's; tests/unit/test_line_splits.py exempts their files until they convert together

**Found 2026-10-05 by `PL-4YVK`.** CommonMark ends a line at `\n`, `\r` or
`\r\n` only (spec 0.31.2, section 2.2), so `splitlines()` is as wrong for a
Markdown reader as for git's output: a U+2028 in a brief would split one line in
two and shift every line index after it. `PL-4YVK` converted every other reader
in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/` to
`docket.lines.split_lines` and left these, listed in
`tests/unit/test_line_splits.py`'s `MARKDOWN_READERS`, for two reasons: their
indices pair with `docket/fences.py`'s, so one converted alone would disagree
with the rest on which line is which; and `#1358` (`PL-R417`'s Markdown readers)
was rewriting most of them, adding three more `splitlines()` calls to
`tools/doc_check.py`. No tracked file holds such a character (measured
2026-10-05), so the change is latent.

**Done when.** After `#1358` lands, every file in `MARKDOWN_READERS` splits with
`split_lines` (a `keepends` form for `fences.without_fences`, `doc_check`'s code
spans and `checks.py`'s statement reader), `fences.py`'s "A line is what
`str.splitlines()` cuts" says `\n`, and `MARKDOWN_READERS` is gone, so the
guard refuses `splitlines()` everywhere in the three trees.
