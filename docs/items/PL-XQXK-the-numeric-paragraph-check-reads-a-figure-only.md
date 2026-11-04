---
id: PL-XQXK
title: The numeric-paragraph check reads a figure only in the units PROSE_UNITS lists (L/min, L, %, kg, s, MAC and time words), so a paragraph stating px, mL, mmHg or percentage points is no member: decide whether to widen PROSE_UNITS, which widens check_untied_restatements too
priority: P3
effort: S
status: done
classes: defect
feature: model-claims-held-by-tests
milestone: v0.6.15
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md, docs/items/PL-19W8-hold-docs-model-md-known-limitations-numeric.md, docs/items/PL-5L84-docs-model-md-states-the-20-c-reference.md, docs/items/PL-ZDZ0-docs-model-md-displayed-precision-says-a-reader.md, docs/items/PL-BSYT-apply-the-prose-review-s-rewrites-of-four-docs.md
deferred-from: v0.7.0 - workflow tooling outside the schematic release
added: 2026-11-02
closed: 2026-11-03
pr: 1976
payoff: a figure in px, mL, mmHg or percentage points in the model documentation is read with its unit, so a numeric claim in those units is held to a test and a volume restated in millilitres is tied to its stored litres
verify: grep -q 'def test_a_figure_in_each_unit_the_documents_write_is_read_with_that_unit' tests/unit/test_doc_check.py
---

**Problem.** The numeric-paragraph check reads a figure only in the units PROSE_UNITS lists (L/min, L, %, kg, s, MAC and time words), so a paragraph stating px, mL, mmHg or percentage points is no member: decide whether to widen PROSE_UNITS, which widens check_untied_restatements too

**Why it matters.** A paragraph that states a value in px, mL, mmHg or percentage points is not checked against its source. Widening `PROSE_UNITS` also widens `check_untied_restatements`, which may raise new findings across the documents.

**Decision needed.** Whether to widen `PROSE_UNITS`, and to which units. **Recommendation: none yet.** The answer rests on a count nobody has taken: how many paragraphs state a value in each missing unit, and how many new findings widening would raise. Taking that count is the first step. The decision is a session's, because its effect stays inside one check.

**Done when.** `PROSE_UNITS` is widened to the units the count shows are used, with a test for each, or the brief records the count and why the list stays as it is.

**Generator check.** One-off. `PROSE_UNITS` is a hand-written list of the units prose may carry. `DisplayUnit` in `src/anesthesia_sim/app/display_units.py` may hold some of the same units, which would make the list a second copy. The session that takes the count checks that.

**Counted and decided, 2026-11-03: widen it.** The count the decision waited on was taken on `main` at `4620917c`. After a number, `docs/MODEL.md` and `README.md` write px 68 times, °C 60, mL 58, mmHg 28, pp 25, ml 23, percentage points 14, g 13, kPa 3, atm 3 and mL/kg once. Widening `PROSE_UNITS` to all of them, with millilitres converted to litres, raised eleven findings in `docs/MODEL.md` and none in `README.md`. Every one was real:

1. Three paragraphs of § "Displayed precision" stated a resolution in percentage points or mL vapour and named no test. Two have tests, which the paragraphs now name. The per-agent figures for one count of the MAC line have none, so that paragraph declares `no test yet (PL-19W8)`.
2. Three `not-restated:` markers declared figures in mL or percentage points. Read bare, those figures had looked like stored coefficients. The markers are removed.
3. "Davis and Mapleson's 1222 ml" restated the stored venous pool, 1.222 L, and "a 10 mL lung" restated the envelope's smallest volume, 0.01 L. Neither was tied to its home. Each now carries a `provenance:` marker.
4. "One count of 10 mL", "<10 mL" and "9.7 to 10.0 mL" only coincide with the envelope's smallest volume. A `not-restated:` marker says so.

A percentage point is the difference between two percents, so it is read as its own unit and never compared with a stored percent. The units no value is stored in are `UNSTORED_UNITS` in `tools/doc_check.py`.

**Generator check, answered.** `DisplayUnit` in `src/anesthesia_sim/app/display_units.py` is not a second copy of this list. It holds the units the interface shows beside a value. `PROSE_UNITS` holds the units the documents write after a number, which include px, mmHg, kPa and °C that the interface never shows.

**Blind review, 2026-11-03.** Both passes found that listing °C and grams as units no value is stored in was wrong. Agent files store the density's reference temperature in °C, its density in g/mL and its molar mass in g/mol. Read as °C, "measured at 20.0 °C" could never match the stored 20.0 again. The fix reads g/mL and g/mol as stored units (`UNIT_ENDINGS`), leaves °C and plain grams in no list, so a figure in them stays a bare number as before, and files `PL-5L84` to tie the 29 "20 °C" paragraphs and then read °C. One pass also found millilitres per minute unread. They are now converted to L/min, and the seven flows in `docs/MODEL.md` raised no finding.
