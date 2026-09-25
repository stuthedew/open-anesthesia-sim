---
id: PL-5XKP
title: glyph_check refuses the non-ASCII key of a str.maketrans normaliser whose purpose is to remove that glyph, and passes chr(0x2192) built inside an f-string
priority: P3
effort: S
status: ready
classes: defect
feature: exact-gates
touches: tools/glyph_check.py, tests/unit/test_glyph_check.py
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
payoff: code that strips an undrawable character from displayed text either passes glyph_check or meets a written reason it cannot, and the chr() blind spot is recorded where the next session reads it
verify: grep -q 'def test_a_translation_table_key' tests/unit/test_glyph_check.py
---

**Problem.** glyph_check refuses the non-ASCII key of a str.maketrans normaliser whose purpose is to remove that glyph, and passes chr(0x2192) built inside an f-string

Reproduced both directions: `str.maketrans({"→": "->"})` fails; `f"{chr(0x2192)}"` passes.

Re-confirmed 2026-09-25 against 46954a81 in a scratch tree: the translation-table key is refused as U+2192 not confirmed to render, and the label built with `chr(0x2192)` is not reported. The two halves meet: `chr()` is the spelling a session refused on the first would reach for, and it is the one the check cannot see. `python_strings`' docstring already says an interpolated value goes unchecked; a `chr()` call outside an f-string is not mentioned anywhere. The `verify:` greps a test-name prefix, so it holds whichever side of the Done-when's either/or the work takes.

**Generator check.** One-off, and removed from PL-GPJ7's `root-cause-of`: the fact misread is whether a string literal reaches a reader, which glyph_check answers by AST structure - every non-docstring literal, default-deny by its stated design - rather than by wording, and both reproductions turn on dataflow a static walk cannot follow. No head's `misread:` states it.

**Why it matters.** A false refusal on the fix for the thing the check exists to prevent, and a false pass on the same glyph spelled another way.

**Done when.** A literal used only as a translation-table key is accepted, or the check documents why not; the `chr()` gap is recorded as known.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
