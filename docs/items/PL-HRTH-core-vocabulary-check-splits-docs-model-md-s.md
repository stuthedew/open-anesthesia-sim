---
id: PL-HRTH
title: core_vocabulary_check splits docs/MODEL.md's Symbols table on every pipe, so a GFM-escaped \| inside a Symbol cell shifts every later column
status: untriaged
feature: exact-gates
touches: tools/core_vocabulary_check.py, tests/unit/test_core_vocabulary_check.py
added: 2026-09-25
---

**Problem.** core_vocabulary_check splits docs/MODEL.md's Symbols table on every pipe, so a GFM-escaped \| inside a Symbol cell shifts every later column

Reproduced with one escaped pipe in a Symbol cell: the check reads the wrong column as the Python name.

**Why it matters.** Hard error, or worse a silent misread of the column that ties a symbol to its code name.

**Done when.** Escaped pipes are honoured when splitting; a test holds a cell containing `\|`.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
