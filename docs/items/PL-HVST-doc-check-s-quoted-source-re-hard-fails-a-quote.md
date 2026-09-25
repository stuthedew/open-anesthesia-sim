---
id: PL-HVST
title: doc_check's QUOTED_SOURCE_RE hard-fails a quote set beside a document name by a possessive, colon, comma, parenthesis or no connective, so proposed or since-deleted wording quoted beside CLAUDE.md fails make check; 422 of 465 matches already use the explicit section mark
status: untriaged
feature: exact-gates
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-25
---

**Problem.** doc_check's QUOTED_SOURCE_RE hard-fails a quote set beside a document name by a possessive, colon, comma, parenthesis or no connective, so proposed or since-deleted wording quoted beside CLAUDE.md fails make check; 422 of 465 matches already use the explicit section mark

Reproduced: an item quoting proposed wording as `` `CLAUDE.md`: "Hand off at 120,000..." `` and one quoting since-deleted wording both fail. Both false refusals came through the non-`§` connectives; the 43 matches using them (possessive 16, none 10, comma 8, colon 4, under 3, paren 2) are the one-time rewrite cost of going `§`-only.

**Why it matters.** A hard gate refusing correct prose teaches sessions to reword rather than to read, which `CLAUDE.md` retires a check for.

**Done when.** Only `§` forms are hard errors; the other connectives are an advisory or not read; a test holds a quoted proposal through a clean run.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
