---
id: PL-TCD3
title: A numeric paragraph passes check_bound_families on any marker in its scope, even a not-restated: marker, which says its figure is tied to nothing, or a marker that ties a different figure: decide whether a marker should hold only the figures it names
priority: P1
effort: S
status: done
classes: docs, science
feature: model-claims-held-by-tests
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md, docs/items
deferred-from: v0.7.0 - filed 2026-11-02 from PL-B6YV's blind review; a question about the check's rule that the schematic does not wait on
added: 2026-11-02
closed: 2026-11-02
pr: 1934
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
- A `derived:` marker ties its computed figure in the unit the marker
  writes, read by `_untied_figures` and compared through `_prose_figure`, and
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
annotated. "Why not a significant-figures rule" declares
``no test yet (`PL-TDX0`)``, because its SDs are wrong (below). "Precision
elsewhere in the interface" names the three slider tests that read 0.1 L/min
from each label, and the test that holds the slider steps. The residual
paragraph is dated to its 2026-10-03 replay and names the four tests that pin
the residual's form.

**Blind review, two passes, 2026-11-02.** Each finding was checked against
the code or the source before acting on it.

- Pass 1 F1 and pass 2 F2 (should-fix): the first build cited Yasuda, Targ and
  Eger for "3.9% to 6.4% of the mean". Those are the paper's brain:blood SDs.
  The fat tissue:gas SDs the agent files quote are 16.7% to 19.2%. The
  citation was reverted, both paragraphs that state the SDs now say so, and
  the correction is filed as `PL-TDX0` (P1, science).
- Pass 1 F2 and pass 2 F1 (should-fix): a `derived:` marker tied a figure by
  its number alone, so "6 L" tied "6 %". Fixed as above, with a case in
  `test_marker_held_figures_names_what_each_marker_kind_ties`.
- Pass 2 F3 and pass 1 F4 (should-fix and optional): `_untied_figures` read
  "86 400 s" as "400 s" and "9.6e-12 s" as "12 s". Fixed in the shared
  reader: a grouped number is read whole, and a number in e-notation is read
  as no figure. Read whole, six figures in `docs/MODEL.md` turned out to
  restate `MAXIMUM_ELAPSED_SIMULATION_TIME_S` or `MAXIMUM_VOLUME_L` with no
  marker, which `check_untied_restatements` had missed. Five got a
  `provenance:` marker. The 10 000 L circuit measured on 2026-09-06 got a
  `not-restated:` marker, because it describes a measured case and would not
  change if the limit did. Reading e-notation whole was not done, because it
  would also need `ASSERTION_RE` and `check_prose_provenance` to read it.
- Pass 2 F4 (should-fix): the residual paragraph named a test that pins only
  one pair of values. It now names the four tests that pin the form.
- Pass 1 F3 (optional): the residual paragraph says every residual was below
  2.1 × 10⁻¹¹ L, and `PL-3PJZ` records the largest as 2.13e-11 L. Left as it
  is, because `PL-KXW1` records 5.4e-11 L for what may be the same quantity,
  and `PL-19W8` already owns saying which. Recorded there.

**Regression test.** `test_a_marker_holds_a_numeric_paragraph_only_through_the_figures_it_ties`,
run against `origin/main`'s `tools/doc_check.py`, fails with
`assert {3, 6, 9, 12, 15, 17} == {9, 15, 17}`. Against this branch's first
build, the review's two cases fail too:
`test_marker_held_figures_names_what_each_marker_kind_ties` with
`assert {('6', '%'), ('6', 'L')} == {('6', 'L')}`, and
`test_a_grouped_figure_is_read_whole_and_an_e_notation_one_as_no_figure` with
`assert [('400', 's'), ('12', 's')] == [('86400', 's')]`.

**What it costs the later passes, counted 2026-11-02.** Across the whole
document, 200 of 385 numeric paragraphs are held by nothing, where 87 were
before. In a sample of 13 of the other 113, 9 had an untied figure that is a
claim. `PL-19W8` records the sample. The tightening was worth taking only if
most of the paragraphs it adds hold a real claim, and on that sample they do.
