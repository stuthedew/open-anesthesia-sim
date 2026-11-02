---
id: PL-TCD3
title: A numeric paragraph passes check_bound_families on any marker in its scope, even a not-restated: marker, which says its figure is tied to nothing, or a marker that ties a different figure: decide whether a marker should hold only the figures it names
priority: P1
effort: S
status: needs-decision
classes: docs, science
feature: model-claims-held-by-tests
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md, docs/items
deferred-from: v0.7.0 - filed 2026-11-02 from PL-B6YV's blind review; a question about the check's rule that the schematic does not wait on
payoff: a computed figure in a section the check holds cannot pass on a marker written for a different figure
added: 2026-11-02
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

**Done when.** The decision is recorded here. If adopted,
`_holds_its_figures` holds a paragraph through a marker only for the figures
the marker names, with unit tests, and every section in `BOUND_FAMILIES`
still conforms.
