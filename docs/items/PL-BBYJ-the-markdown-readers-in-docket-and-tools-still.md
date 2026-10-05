---
id: PL-BBYJ
title: The Markdown readers in docket and tools still split with str.splitlines(), which breaks at U+2028, U+0085 and form feed where CommonMark ends no line, and pair their line indices with fences.py's; tests/unit/test_line_splits.py exempts their files until they convert together
priority: P3
effort: M
status: ready
classes: defect
feature: line-ends
touches: subprojects/docket/src/docket/lines.py, subprojects/docket/src/docket/fences.py, subprojects/docket/src/docket/markdown.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/instructions.py, subprojects/docket/src/docket/notes.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/roadmap.py, tools/doc_check.py, tools/dead_ends.py, subprojects/docket/tests, tests/unit, docs/items/PL-4YVK-readers-split-line-oriented-text-with-str.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-05
payoff: A brief, the roadmap or a document holding a pasted U+2028 or form feed is read as the lines GitHub renders, so no reader conjures a heading, fence or thread from one or reports a line past it one too high, and no reader in the apparatus can reach for splitlines() again
verify: ! grep -qF 'MARKDOWN_READERS' tests/unit/test_line_splits.py && grep -q 'def test_a_fence_is_read_from_lines_cut_at_a_newline_alone' subprojects/docket/tests/test_fences.py
---

**Problem.** The Markdown readers in docket and tools still split with str.splitlines(), which breaks at U+2028, U+0085 and form feed where CommonMark ends no line, and pair their line indices with fences.py's; tests/unit/test_line_splits.py exempts their files until they convert together

**Found 2026-10-05 by `PL-4YVK`.** CommonMark ends a line at `\n`, `\r` or
`\r\n` only (spec 0.31.2, section 2.1), so `splitlines()` is as wrong for a
Markdown reader as for git's output: a U+2028 in a brief would split one line in
two and shift every line index after it. `PL-4YVK` converted every other reader
in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/` to
`docket.lines.split_lines` and left these, listed in
`tests/unit/test_line_splits.py`'s `MARKDOWN_READERS`, for two reasons: their
indices pair with `docket/fences.py`'s, so one converted alone would disagree
with the rest on which line is which; and `#1358` (`PL-R417`'s Markdown readers)
was rewriting most of them, adding three more `splitlines()` calls to
`tools/doc_check.py`. No tracked Markdown file holds such a character (measured
2026-10-05), so the change is latent.

**Why it matters.** A reader that ends a line where CommonMark does not reads a
different document from the one GitHub renders and its writer sees: a U+2028 or
a form feed puts what follows it at a line's start, where it can open a heading,
a fence or a list item nobody wrote, and every line index after it moves by one.
These readers read the item briefs, `ROADMAP.md`, `docs/WORKING_NOTES.md`, the
instruction set and every document `tools/doc_check.py` holds to the tree, so one
pasted character can conjure a milestone section or a working-notes thread, hide
the citations under a fence nobody opened, or report a finding on the wrong
line. And the exemption is the opening the guard was built to close: while eight
files may call `splitlines()`, a reader added to any of them is free to reach for
it again, as four readers did before `PL-4YVK`.

**Reproduced at triage, 2026-10-05**, on python3 3.11.15 with `docket` at
`034220ea` (the claim on `100ad9b4`). A working-notes file of four lines, the
first holding a U+2028:

```text
Intro<U+2028>## A thread nobody wrote
More prose.

## The real thread
```

`notes.read` returns two threads, "A thread nobody wrote" at line 2 and "The
real thread" at line 5; cut at `\n` the same text holds one heading, on line 4.
CommonMark agrees with the cut at `\n`: markdown-it-py 4.2.0 renders the first
two lines as one paragraph, renders a form feed, a U+0085 and a `\x0b` inside a
line as text, and ends a line at a raw `\r`. Every text these readers are handed
is decoded with that `\r` already made a `\n` - `read_text`,
`subprocess.run(text=True)` and `vcs`'s blob batch all translate - so a cut at
`\n` alone is CommonMark's cut on all of them. Of 2,702 tracked UTF-8 files, only
`subprojects/docket/tests/test_lines.py` holds one of those characters, on
purpose, and no Markdown reader reads it; none holds a raw `\r`. The change is
latent.

**Three readers of other formats share the exemption.** It was by file, so it
also covered `tools/doc_check.py`'s `_deleted_paths` (git's `log --name-only`
output), `_make_lines` (a Makefile) and `workflow_commands` (a workflow's YAML).
None of those formats ends a line at the characters either: git breaks its
output at newlines, YAML 1.2.2 section 5.4 makes a form feed, U+0085, U+2028 and
U+2029 non-break characters, and GNU make 4.3 ran a recipe line holding a form
feed, a U+2028 and a U+0085 as one line (measured 2026-10-05). They convert with
the rest, 37 calls in eight files.

**Generator check.** A member of `PL-4YVK`, filed while that head is open and
already in its `root-cause-of:`: where one line ends in line-oriented text, here
a Markdown document, the fact the head's `misread:` names. Not a re-entry and
not a post-close instance: the head left these files exempt on purpose until
`#1358` landed.

**Done when.** Every file `MARKDOWN_READERS` lists splits with `split_lines`,
whose `keepends` form serves `fences.without_fences`, `doc_check`'s `_code_spans`
and `_statement_offsets` and `checks.py`'s `_line_starts`; `fences.py`'s and
`markdown.py`'s "A line is what `str.splitlines()` cuts" say what `split_lines`
cuts; `MARKDOWN_READERS` is gone, so the guard refuses `splitlines()` everywhere
in the three trees; and each converted module has a test, failing against its
old reader, that reads a line holding a U+2028 or a form feed as one line.

**`#1358` landed, 2026-10-05.** It merged as `f84e31f9` and took the last
`splitlines()` call out of `tools/core_vocabulary_check.py`, which
`test_every_exempt_file_still_needs_its_exemption` caught on the base merge
into `#1364`, so that file left `MARKDOWN_READERS` there. `docket/markdown.py`,
which `#1358` added, calls none. The wait above is over.
