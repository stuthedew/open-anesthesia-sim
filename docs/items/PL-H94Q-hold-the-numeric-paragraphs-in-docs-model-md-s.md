---
id: PL-H94Q
title: Hold the numeric paragraphs in docs/MODEL.md's model sections (selected method, alveolar gas, mass balance, agent amount, concentrations) to named tests
priority: P1
effort: S
status: done
classes: docs, science
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tools/doc_check.py, tests, docs/items
blocked-by: PL-19W8
deferred-from: v0.7.0 - not live: checked 2026-11-07 (PL-8C8W): the paragraphs it would hold are docs/MODEL.md prose that no displayed string carries, so no learner can see a wrong value now
added: 2026-11-02
closed: 2026-11-22
pr: 2255
payoff: the numbers in the model sections of docs/MODEL.md are computed by a named test, so a wrong one fails the build rather than waiting for a reader
tests: tests/reference/test_published_vapour_to_liquid.py::test_the_agent_amount_section_prints_what_its_inputs_give, tests/unit/test_concentration.py::test_a_round_trip_through_a_fraction_misses_the_dialled_percent_at_126_of_801_positions, tests/unit/test_agent_simulation_validation.py::test_the_running_agent_totals_stay_within_a_tenth_of_the_accounting_tolerance
---

**Problem.** These `docs/MODEL.md` sections state figures with a unit in
paragraphs that carry no test, marker, source or date. Counted 2026-11-02
with `_numeric_paragraph_members`, as unheld of numeric paragraphs:

- "Selected method (as implemented)", "Alveolar gas", "Mass-balance
  identity", "Agent amount" and "Concentrations": 1 each

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

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present in part when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. It stays deferred to the next gate: its `deferred-from:` records the check that no learner can see a wrong value now (`PL-8C8W`). Four of the five paragraphs were in `docs/MODEL.md` at `817a4d88`. The agent-amount paragraph came with `c95177a6` (2026-10-26).

**Checked 2026-11-22** against `d4e8200`: still applies, and more is unheld than the brief counts. A recount on 2026-11-22 with the check's own reader, `_numeric_paragraph_members`, finds these numeric paragraphs with no test, source, date or marker: "Selected method (as implemented)" 9 of 20, "Alveolar gas" 6 of 9, "Mass-balance identity" 2 of 6, "Agent amount" 8 of 12 and "Concentrations" 2 of 3. None of the five headings is in `BOUND_FAMILIES` in `tools/doc_check.py`. The blocker `PL-19W8` is done. "Selected method" sits under "Numerical method" and "Mass-balance identity" under "Conservation of agent mass", and `PL-6PPZ` (claimed elsewhere) moves both of those sections to a new verification document. So build this pass after that move, and point its families at the file the sections then live in.

**Closed 2026-11-22.** The four sections that still had unheld numeric paragraphs are in `BOUND_FAMILIES`: "Mass-balance identity", "Selected method (as implemented)" and "Concentrations" in `docs/VERIFICATION.md`, and "Agent amount" in `docs/PARAMETERS.md`. Every numeric paragraph in them now names its test or cites its source. "Alveolar gas" in `docs/MODEL.md` no longer has a numeric paragraph, so it needs no family. New tests: `test_the_agent_amount_section_prints_what_its_inputs_give` recomputes the agent-amount section's molar volume, density and molar-mass figures, with Laster's halothane and enflurane densities (*Anesth Analg* 1994;78(6):1152-3) and ChEMBL molar masses read on 2026-11-22. `test_a_round_trip_through_a_fraction_misses_the_dialled_percent_at_126_of_801_positions` checks the concentrations section's round-trip figure.

Computed claims found wrong or missing a condition: two. The agent-amount section said a run at 37 °C reads "5.1–6.3 %" high. The recomputed range is 5.1–6.2 %, and the 6.3 came from a rounded intermediate. The running-totals test in `tests/unit/test_agent_simulation_validation.py` still assumed the retired 1 ms step. It now runs the full day of 86 400 one-second steps at the largest transfer per step. The mass-balance headroom "about 250×" is now the measured 256×, dated.

Files checked in the sweep: `docs/MODEL.md`, `docs/PARAMETERS.md`, `docs/VERIFICATION.md`, `docs/INTERFACE.md` and `README.md`, for "6.3 %", "about 250" and the 1 ms step. None remained.
