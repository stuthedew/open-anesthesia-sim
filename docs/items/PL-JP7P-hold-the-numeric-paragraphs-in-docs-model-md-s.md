---
id: PL-JP7P
title: Hold the numeric paragraphs in docs/MODEL.md's interface sections (hover readout, MAC-awake, MAC multiples, time base, control-input record and five smaller sections) to named tests
priority: P1
effort: M
status: done
classes: docs, science
feature: model-claims-held-by-tests
milestone: v0.6.22
touches: docs/MODEL.md, docs/INTERFACE.md, tools/doc_check.py, tests, docs/items
blocked-by: PL-19W8
deferred-from: v0.7.0 - not live: checked 2026-11-07 (PL-8C8W): the paragraphs it would hold are docs/MODEL.md prose that no displayed string carries, so no learner can see a wrong value now
added: 2026-11-02
closed: 2026-11-23
pr: 2268
payoff: the numbers in the interface sections of docs/MODEL.md are computed by a named test, so a wrong one fails the build rather than waiting for a reader
tests: tests/unit/test_doc_check.py::test_the_interface_document_is_one_numeric_family_from_its_first_heading, tests/reference/test_interface_figures.py::test_the_hover_s_percent_is_the_mac_multiples_printed, tests/reference/test_interface_figures.py::test_the_hover_s_fat_values_after_a_fork_are_the_ones_printed
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

**The rule.** `docs/VERIFICATION.md` § "How this document is held to the tree"
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

[superseded 2026-11-14: PL-19W8 closed and found five wrong claims, so this pass runs]
**Blocked on `PL-19W8`, the first pass.** If that pass finds no computed
claim wrong or missing a condition in "Known limitations" and "Displayed
precision" together, this item is dropped and the check stays on those two
sections (`PL-B6YV` § "What would make this wrong").

**Done when.** Each section above is in `BOUND_FAMILIES` with
`_numeric_paragraph_members`, every one of its numeric paragraphs carries an
accepted form, and this brief records how many computed claims the pass
found wrong or missing a condition.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present in part when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. It stays deferred to the next gate: its `deferred-from:` records the check that no learner can see a wrong value now (`PL-8C8W`). Every paragraph it counts was in `docs/INTERFACE.md` at `817a4d88` except § "A preview of an unapplied setting" (`f466af3a`, 2026-11-01). The MAC-awake paragraph's 0.84 MAC figure came with `5a8dc036` (2026-10-26).

**Checked 2026-11-22** against `d4e8200`: still applies, and more is unheld than the brief counts. Every section it names is now in `docs/INTERFACE.md`, moved by #2109 (`PL-CTXZ`). A recount on 2026-11-22 with `_numeric_paragraph_members` finds: the hover readout 18 of 22, MAC-awake 13 of 15, MAC multiples 12 of 14, the control-input record 4 of 7, the time base 2 of 2, "What this list requires once the layout is the reader's" 3 of 7, "Interface boundary" 5 of 14, "Halting on a marked crossing" 6 of 7, "Agent-change behavior" 1 of 1 and "A preview of an unapplied setting" 1 of 3. "Minimum displayed outputs" read whole, with its subsections, has 70 of 130 unheld. That heading is already a family that checks its list entries name a test, so a numeric family on it would also read its subsections. None of these headings is a numeric family in `BOUND_FAMILIES`.

**Done 2026-11-23.** One numeric family now reads the whole of
`docs/INTERFACE.md`, under its level-1 heading "Interface requirements", in
place of the two families on "Displayed precision" and "Supported input
ranges". So a figure added to any section later fails the check until it names
a test, a source or a date. The recount at the start found 69 unheld
paragraphs; none is left.

The pass found six computed claims wrong or stale, and fixed each:

1. The hover readout's 1.43% was printed as 0.71 MAC of sevoflurane and
   0.24 MAC of desflurane. It is 0.79 and 0.22.
2. The hover worked examples printed values from a run at a 2.0% dial
   labelled as sevoflurane at 1 MAC: an alveolar 1.43% at 0.71 ×MAC, and
   muscle at 0.19% and 0.10 ×MAC at 20 min. The default case at its stored
   1 MAC gives 1.28% at 0.71 ×MAC, and muscle at 0.14% and 0.08 ×MAC. The
   cause was the unit-test fixtures in `tests/unit/test_chart_frame.py`,
   which labelled a 1 MAC of 2.0% as sevoflurane and typed the fractions by
   hand; the document's examples were copied from their output. The fixtures
   now take their fractions from runs of the model (`_case_at_twenty_minutes`)
   and use the stored MAC, axis and band, and the tests read the examples
   from the document rather than a typed copy. The first pass of this item
   changed only the ×MAC figures; both blind review passes found that the
   percents were still the 2.0% run's.
3. The modelled fat values after the fork at 3492 s were printed as 0.031%
   and 0.006%. A run gives 0.028% and 0.005%.
4. § "How a branch is drawn" said all 8 of the branch's columns are the
   trunk's and 2 of 8 fall on the grid. The branch now draws extremum columns
   too, so the counts were stale; the sentence now states the property
   without them.
5. The schematic said the circuit rises "towards 4 MAC" at sevoflurane's 8%
   maximum. It is 4.44 ×MAC.
6. Tests in `tests/unit/test_formatting.py` and
   `tests/integration/test_qt_chart.py` named sevoflurane or desflurane and
   used another MAC (2.0% and 6.0%), so they printed a MAC-awake band of
   0.58-0.78% for sevoflurane. They now use 1.8% and 6.6%, which give
   0.52-0.70%. The `HEIGHT_BAND` docstring in `core/rounding.py` has the same
   stale 2.0% and is filed as `PL-SLFT`, because a defect in `core/` is filed
   rather than fixed in place.

New tests: `tests/reference/test_interface_figures.py` computes each figure
that no existing test computed (15 tests), and
`test_the_references_answer_no_hover_and_clear_space_answers_none` now also
checks the MAC-awake band and a control mark. Figures from a published source
cite it: Mapleson 1996 by PMID 8777094, read as the abstract through PubMed;
the *Workbook for Gas Man* by its printed pages, read from the private
reference corpus on 2026-11-23 (pp. 105, 141, 171, 172 and 174). Two figures
that were one-off measurements are now dated: 94.3% (2026-09-22, `PL-KRZW`,
commit `67923625`) and 0.2-1.4 px (2026-09-19, `PL-QYBW`).

Files checked in the sweep: `docs/INTERFACE.md` whole, `docs/VERIFICATION.md`,
`docs/MODEL.md`, `docs/PARAMETERS.md`, `README.md` and `ROADMAP.md`, searched
for each wrong figure above; none repeats it.

**Merge review, 2026-11-23.** No value the simulator computes or shows
changes, because no file under `src/` changes. Every figure this change
rewrites in `docs/INTERFACE.md` is restated from what its own tests measure,
and no sentence changes what a value means or what a limitation promises. So
the owner's read is not needed, and the pull request merges on green.

**Main merged, 2026-11-23.** The reader-chosen chart top (#2270) merged
while this was open. Its new paragraphs on the three tops, the gridlines, the
percent labels and the high top's margin over the vaporizer maxima now name
the tests that compute their figures. A schematic paragraph names main's
renamed marks test. No sentence changed what a value means, so the owner's
read is still not needed.
