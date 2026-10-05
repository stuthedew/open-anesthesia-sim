---
id: PL-4YVK
title: Readers split line-oriented text with str.splitlines(), which also breaks at characters that git's output, a JSON-lines transcript, a log record and Python source do not end a line at: PL-139L, PL-PK4B, PL-K1D6 and PL-LRBV are one fact
priority: P1
effort: M
status: done
classes: defect
feature: line-ends
touches: subprojects/docket/src/docket, tools, .claude/hooks/stop_hook_patch.py, subprojects/docket/tests, tests/unit, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-05
pr: 1369
payoff: a ref, a transcript record or a log entry is read as the one line its format wrote, so no reader answers from a partial reading it does not name
verify: grep -q '^generator: spent' docs/items/PL-4YVK-*.md && ! grep -qF '"subprojects/docket/src/docket/fences.py",' tests/unit/test_line_splits.py
root-cause-of: PL-139L, PL-PK4B, PL-K1D6, PL-LRBV, PL-BBYJ, PL-0R4M
generator: spent - tests/unit/test_line_splits.py refuses splitlines() everywhere in tools/, docket and .claude/hooks since PL-BBYJ converted the Markdown readers, and refuses text-mode decoding on every subprocess call there but four listed non-git runners (PL-0R4M), so a new git, transcript, log or Markdown reader can pick neither
misread: Where one line ends in line-oriented text: git output, a JSON-lines transcript, a log, Python source
---

**Problem.** `str.splitlines()` breaks at `\x0b`, `\x0c`, `\x1c`-`\x1e`, `\x85`,
U+2028 and U+2029 as well as at newlines, and none of the line-oriented formats
this apparatus reads ends a line there: git breaks its output only at newlines,
a JSON-lines transcript only at `\n` (JSON leaves U+2028 raw), and Python's
tokenizer only at newlines. Four readers have misread it:

- `PL-139L` (done 2026-09-26): `vcs`'s subject-bearing log reads.
- `PL-PK4B` (ready): `fixture_id_check.scan_python` rebuilds source from
  `splitlines()` before `ast.parse`, so legal source crashes `make check`.
- `PL-K1D6`: `vcs`'s ref-name reads, the sibling sites `PL-139L`'s fix did not
  reach, and `context_reading.read`.
- `PL-LRBV`: the item-read log, whose writer strips two characters and whose
  reader breaks at more.

**Why it matters.** Each reader answers from a partial reading it does not
name: a ref read as two names drops out of `unlanded`, a transcript record read
as two is dropped from the spend, a log target comes back cut short. The four
were filed by four different sessions, and 33 files under `tools/`,
`subprojects/docket/src/docket/` and `.claude/hooks/` still call
`splitlines()` (measured 2026-10-04), so each new reader of line-oriented text
is free to pick it again.

**Done when.** The four members are closed with their own tests; every reader
of git's output, a transcript or a log record under those three trees splits
where its format ends a line, through one function per format or a guard test
that refuses a bare `splitlines()` on such text; and `generator:` is rewritten
`spent` with the reason.

**Generator check.** The head: one fact, where a line ends, misread by four
items, which no head's `misread:` stated on 2026-10-04. `PL-139L`'s and
`PL-PK4B`'s own checks set the count. Not `PL-R417`'s, which is the opposite
reading: a statement its format continues, read as one line.

**Progress, 2026-10-05.** `docket.lines.split_lines` breaks at `\n` alone and
reads what `splitlines()` read on every file in the tree. Every git, transcript,
log and Python-source reader under the three trees now splits with it, or with
`str.split("\n")`/`partition` in a tool that does not import docket, and
`tests/unit/test_line_splits.py` refuses a `splitlines()` call in those trees
outside `MARKDOWN_READERS`. `PL-K1D6`, `PL-PK4B` and `PL-LRBV` closed with their
own tests, each shown failing against the old readers. Two members were found
and filed, and hold the head open: `PL-BBYJ`, the Markdown readers, which wait
for `#1358`; and `PL-0R4M`, the text-mode decoding that cuts a git record at a
raw `\r` before any reader splits it. The `generator:` line says why it is
still `live`.

**`PL-BBYJ`, 2026-10-05.** The Markdown readers split with `split_lines` too,
and so do `tools/doc_check.py`'s readers of git's `log --name-only`, a Makefile
and a workflow's YAML, which shared their exemption. `MARKDOWN_READERS` is gone,
so `tests/unit/test_line_splits.py` refuses `splitlines()` everywhere in the
three trees.

**Closed 2026-10-05, in `#1369`.** `PL-0R4M` merged first, in `#1368`, so with
`PL-BBYJ` closed all six members are closed, `generator:` reads `spent` with
both guards as its reason, and the `verify:` command passes. `docket check`
refuses an open item whose command passes, so the head closes in the second of
the two pull requests rather than in one of its own.
