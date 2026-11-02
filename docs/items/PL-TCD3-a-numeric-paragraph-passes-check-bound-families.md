---
id: PL-TCD3
title: A numeric paragraph passes check_bound_families on any marker in its scope, even a not-restated: marker, which says its figure is tied to nothing, or a marker that ties a different figure: decide whether a marker should hold only the figures it names
priority: P1
effort: S
status: ready
classes: docs, science
feature: model-claims-held-by-tests
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md, docs/items
deferred-from: v0.7.0 - filed 2026-11-02 from PL-B6YV's blind review; a question about the check's rule that the schematic does not wait on
added: 2026-11-02
payoff: a computed figure in a section the check holds cannot pass on a marker written for a different figure
verify: grep -q 'def _marker_held_figures' tools/doc_check.py && grep -q '_marker_held_figures' tests/unit/test_doc_check.py
---

**Problem.** `PL-B6YV` built the rule as decided: a numeric paragraph passes
`check_bound_families` if it carries a `provenance:`, `derived:` or
`not-restated:` marker. The check asks only whether a marker speaks for the
paragraph, not which figure it ties. So a paragraph with a computed figure
passes on a marker about another figure in it. A `not-restated:` marker
passes it too, though that marker says its figure is tied to no stored
value. Both blind review passes on `#1927` found this on 2026-11-02. In
"Displayed precision", the one-SD shifts of the exhaust total, of a
compartment's amount and of a compartment's share each passed on a marker
for the 24 h limit or for 0.18. They now also declare
``no test yet (`PL-19W8`)``, but nothing makes the next one do so.

**Why it matters.** The rule exists so that a computed figure names the test
that computes it. A pass on an unrelated marker reports the section as held
while that figure is held by nothing, which is the silent wrong answer the
rule was built to end. It also hides such figures from `PL-19W8`'s count,
which decides whether the other passes run.

**Decision needed.** Should a marker hold a numeric paragraph only through the
figures it names?

**Recommendation:** yes. A `provenance:` marker holds the figures equal to the
values it asserts, and a `derived:` marker holds the figure it states it
computed. A `not-restated:` marker holds nothing for this rule. A paragraph
with any other figure in a unit then needs a test, a source, a date or the
declared-none form. `_marker_ties` and `_prose_figure` already read which
figure a marker names, so the check reuses them. It costs more annotation in
each pass, because a paragraph can no longer pass on one marker. It reopens
part of the ratified `PL-B6YV` decision, which listed the three markers as
passing forms, so the choice is the owner's. The alternative is to keep the
paragraph-level rule and rely on each pass to declare the figures a marker
does not cover, as `PL-B6YV` did by hand.

**Decided 2026-11-02 (project owner, 2026-11-02, ratified).** Adopted as
recommended: a marker holds a numeric paragraph only through the figures it
names, and a `not-restated:` marker holds nothing for this rule. It was chosen
over keeping the paragraph-level rule and relying on each pass to declare the
figures a marker does not cover. It reopens, for markers only, the forms
`PL-B6YV` listed. The answer was "agree with recs", so it reopens on ordinary
evidence.

**Done when.** `_holds_its_figures` holds a paragraph through a marker only
for the figures the marker names. A `provenance:` marker covers each figure
equal to a value it asserts, a `derived:` marker covers the figure it states
it computed, and a `not-restated:` marker covers none. A paragraph with any
other figure in a unit needs a test, a source, a date or the declared-none
form. The reader that says which figures a marker covers is
`_marker_held_figures`, built on `_marker_ties` and `_prose_figure`, with
unit tests for each marker kind. Every section in `BOUND_FAMILIES` still
conforms, and any paragraph the change newly fails is annotated in the same
change. If the reader lands under another name, update `verify:` in the same
commit.

**Built 2026-11-02.** `_holds_its_figures` now holds a paragraph in two ways.
A test name, a published source, a date or the declared-none form holds the
whole paragraph, as before. Without one of those, the paragraph passes only
where `_marker_held_figures` says a marker ties every figure with a unit in
it. That reader calls `_marker_ties`, so a marker ties a figure here exactly
as `check_untied_restatements` reads a tie. Four choices were made inside the
agreed approach:

- A `provenance:` marker ties a figure through `_matches`, against the value
  the marker asserts and the unit its key's ending declares. So a marker for
  `volume_l = 6` ties "6 L" and not "6 %". `_MarkerScope` now records the
  asserted values, and its `homes` are read from them, so the two checks read
  one record.
- A `derived:` marker ties its computed figure as the marker writes it, and
  also each input value it asserts. The brief named only the computed figure.
  The inputs are stored values held to their files, as a `provenance:`
  marker's are, and `check_untied_restatements` already ties them.
- A member's lines lose their shared indentation. Without that, a paragraph
  indented four columns inside a list item reads alone as an indented code
  block, which states no figure. A paragraph that yields no figure fails
  rather than passes, so a disagreement between the two readers is loud.
- The family's promise text in `BOUND_FAMILIES` and `docs/MODEL.md` § "How
  this document is held to the tree" now state the rule.

Three "Displayed precision" paragraphs failed under the new rule, and each is
annotated. "Why not a significant-figures rule" cites Yasuda, Targ and Eger
for its 3.9% to 6.4% (Anesth Analg 1989;69:370-373, PMID 2774233, checked in
PubMed's metadata). "Precision elsewhere in the interface" names the three
slider tests that read 0.1 L/min from each label, and the test that holds the
slider steps. The residual paragraph is dated to its 2026-10-03 replay and
names `test_format_agent_residual_prints_no_digit_a_last_bit_change_redraws`.

**Regression test.** `test_a_marker_holds_a_numeric_paragraph_only_through_the_figures_it_ties`,
run against `origin/main`'s `tools/doc_check.py`, fails with
`assert {3, 6, 9, 12, 15, 17} == {9, 15, 17}`.

**What it costs the later passes, counted 2026-11-02.** Across the whole
document, 201 of 386 numeric paragraphs are held by nothing, where 89 were
before. In a sample of 13 of the other 112, 9 had an untied figure that is a
claim. `PL-19W8` records the sample. The tightening was worth taking only if
most of the paragraphs it adds hold a real claim, and on that sample they do.
