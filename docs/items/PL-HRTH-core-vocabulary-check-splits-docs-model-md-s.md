---
id: PL-HRTH
title: core_vocabulary_check splits docs/MODEL.md's Symbols table on every pipe, so a GFM-escaped \| inside a Symbol cell shifts every later column
priority: P3
effort: S
status: ready
classes: defect
feature: exact-gates
touches: tools/core_vocabulary_check.py, tests/unit/test_core_vocabulary_check.py
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
payoff: a Symbols row whose symbol needs a literal pipe, such as an absolute value, is checked against its own Code cell instead of being refused or read from the wrong column
verify: grep -q 'def test_an_escaped_pipe_stays_inside_its_cell' tests/unit/test_core_vocabulary_check.py
---

**Problem.** core_vocabulary_check splits docs/MODEL.md's Symbols table on every pipe, so a GFM-escaped \| inside a Symbol cell shifts every later column

Reproduced with one escaped pipe in a Symbol cell: the check reads the wrong column as the Python name.

Re-confirmed 2026-09-25 against 46954a81: `symbol_cells` splits a row whose Symbol cell holds an escaped pipe into extra cells and reads the Symbol cell's tail as the Code cell. `docs/MODEL.md`'s Symbols table holds no escaped pipe today, so the fault is latent, and the shifted cell fails loudly - `_resolve` finds no `ClassName.accessor` in it - unless the column that lands there happens to hold exactly one, which is the silent case.

**Generator check.** One-off, and removed from PL-GPJ7's `root-cause-of`: the fact misread is where a GFM table cell ends, which the table's own syntax decides exactly, and the split does not implement the escape. No head's `misread:` states it, and recognising by explicit syntax - the head's rule - is already what this gate does.

**Why it matters.** Hard error, or worse a silent misread of the column that ties a symbol to its code name.

**Done when.** Escaped pipes are honoured when splitting; a test holds a cell containing `\|`.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
