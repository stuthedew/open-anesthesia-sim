---
id: PL-JP7P
title: Hold the numeric paragraphs in docs/MODEL.md's interface sections (hover readout, MAC-awake, MAC multiples, time base, control-input record and five smaller sections) to named tests
priority: P1
effort: M
status: blocked
classes: docs, science
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tools/doc_check.py, tests, docs/items
blocked-by: PL-19W8
deferred-from: v0.7.0 - filed 2026-11-02 as an annotation pass of PL-B6YV's rule; docs/MODEL.md traceability work that the schematic does not wait on
added: 2026-11-02
payoff: the numbers in the interface sections of docs/MODEL.md are computed by a named test, so a wrong one fails the build rather than waiting for a reader
verify: grep -q 'heading="MAC multiples as a display unit"' tools/doc_check.py
---

**Problem.** These `docs/MODEL.md` sections state figures with a unit in
paragraphs that carry no test, marker, source or date. Counted 2026-11-02
with `_numeric_paragraph_members`, as unheld of numeric paragraphs:

- "The chart's hover readout: what the tooltip may show": 14 of 20
- "MAC-awake as a chart reference": 5 of 12
- "MAC multiples as a display unit": 4 of 9
- "The control-input record": 4 of 23
- "The chart's time base": 2 of 2
- "What this list requires once the layout is the reader's": 2 of 4
- "Interface boundary": 2 of 7
- "Halting on a marked crossing": 2 of 4
- "Minimum displayed outputs", "A preview of an unapplied setting" and
  "Agent-change behavior": 1 each

**Why it matters.** A figure about what the model computes that no test
computes can be wrong, or lose its condition, and nothing notices.
`PL-B6YV`'s members were seven such sentences.

**The rule.** `docs/MODEL.md` § "How this document is held to the tree"
says a computed claim names the test that computes it (`PL-B6YV`, project
owner, 2026-11-02, ratified). In a section listed in `BOUND_FAMILIES` with
`_numeric_paragraph_members`, `make check` fails each paragraph that states a
number with a unit and carries none of the accepted forms. `PL-B6YV` added
"Displayed precision" as the first such section. Each pass names an existing
test where one computes the claim, writes a test where none does, and
otherwise uses ``no test yet (`PL-XXXX`)`` against an open item. A figure
that is a published value is cited by a DOI, a PubMed id, an ISBN or a
journal locator. The pass then adds its sections to `BOUND_FAMILIES` in the
same change, so the check stays green.

**Blocked on `PL-19W8`, the first pass.** If that pass finds no computed
claim wrong or missing a condition in "Known limitations" and "Displayed
precision" together, this item is dropped and the check stays on those two
sections (`PL-B6YV` § "What would make this wrong").

**Done when.** Each section above is in `BOUND_FAMILIES` with
`_numeric_paragraph_members`, every one of its numeric paragraphs carries an
accepted form, and this brief records how many computed claims the pass
found wrong or missing a condition.
