---
id: PL-XQXK
title: The numeric-paragraph check reads a figure only in the units PROSE_UNITS lists (L/min, L, %, kg, s, MAC and time words), so a paragraph stating px, mL, mmHg or percentage points is no member: decide whether to widen PROSE_UNITS, which widens check_untied_restatements too
priority: P3
effort: S
status: needs-decision
classes: defect
feature: model-claims-held-by-tests
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.7.0 - workflow tooling outside the schematic release
added: 2026-11-02
---

**Problem.** The numeric-paragraph check reads a figure only in the units PROSE_UNITS lists (L/min, L, %, kg, s, MAC and time words), so a paragraph stating px, mL, mmHg or percentage points is no member: decide whether to widen PROSE_UNITS, which widens check_untied_restatements too

**Why it matters.** A paragraph that states a value in px, mL, mmHg or percentage points is not checked against its source. Widening `PROSE_UNITS` also widens `check_untied_restatements`, which may raise new findings across the documents.

**Decision needed.** Whether to widen `PROSE_UNITS`, and to which units. **Recommendation: none yet.** The answer rests on a count nobody has taken: how many paragraphs state a value in each missing unit, and how many new findings widening would raise. Taking that count is the first step. The decision is a session's, because its effect stays inside one check.

**Done when.** `PROSE_UNITS` is widened to the units the count shows are used, with a test for each, or the brief records the count and why the list stays as it is.

**Generator check.** One-off. `PROSE_UNITS` is a hand-written list of the units prose may carry. `DisplayUnit` in `src/anesthesia_sim/app/display_units.py` may hold some of the same units, which would make the list a second copy. The session that takes the count checks that.
