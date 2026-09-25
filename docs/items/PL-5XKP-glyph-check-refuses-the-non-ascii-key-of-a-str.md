---
id: PL-5XKP
title: glyph_check refuses the non-ASCII key of a str.maketrans normaliser whose purpose is to remove that glyph, and passes chr(0x2192) built inside an f-string
status: untriaged
feature: exact-gates
touches: tools/glyph_check.py, tests/unit/test_glyph_check.py
added: 2026-09-25
---

**Problem.** glyph_check refuses the non-ASCII key of a str.maketrans normaliser whose purpose is to remove that glyph, and passes chr(0x2192) built inside an f-string

Reproduced both directions: `str.maketrans({"→": "->"})` fails; `f"{chr(0x2192)}"` passes.

**Why it matters.** A false refusal on the fix for the thing the check exists to prevent, and a false pass on the same glyph spelled another way.

**Done when.** A literal used only as a translation-table key is accepted, or the check documents why not; the `chr()` gap is recorded as known.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
