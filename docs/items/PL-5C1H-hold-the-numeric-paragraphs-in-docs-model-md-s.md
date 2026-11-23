---
id: PL-5C1H
title: Hold the numeric paragraphs in docs/MODEL.md's parameter and range sections (supported input ranges, delivery-limit and MAC parameters, source hierarchy, v0.2.0 agents) to named tests
priority: P1
effort: M
status: done
classes: docs, science
feature: model-claims-held-by-tests
milestone: v0.6.22
touches: docs/MODEL.md, docs/INTERFACE.md, docs/PARAMETERS.md, tools/doc_check.py, tests, docs/items
blocked-by: PL-19W8
deferred-from: v0.7.0 - not live: checked 2026-11-07 (PL-8C8W): the paragraphs it would hold are docs/MODEL.md prose that no displayed string carries, so no learner can see a wrong value now
added: 2026-11-02
closed: 2026-11-22
pr: 2256
payoff: the numbers in the parameter and range sections of docs/MODEL.md are computed by a named test, so a wrong one fails the build rather than waiting for a reader
tests: tests/reference/test_supported_input_range_figures.py::test_alveolar_wash_in_at_five_minutes_quickens_as_cardiac_output_falls, tests/reference/test_supported_input_range_figures.py::test_a_long_sevoflurane_run_leaves_the_measured_exposure_range_as_printed, tests/reference/test_supported_input_range_figures.py::test_the_run_length_is_the_fraction_of_the_fat_time_constant_printed, tests/reference/test_parameter_source_figures.py::test_the_stored_blood_gas_coefficients_sit_below_the_measured_ones_as_printed, tests/reference/test_parameter_source_figures.py::test_the_stored_tissue_coefficients_lie_as_close_to_yasudas_means_as_printed, tests/reference/test_parameter_source_figures.py::test_the_vessel_rich_coefficients_match_yasudas_brain_values_as_printed, tests/reference/test_parameter_source_figures.py::test_storing_yasudas_means_would_move_the_time_constants_as_printed, tests/reference/test_parameter_source_figures.py::test_a_desflurane_percent_over_the_stored_mac_gives_the_figures_printed, tests/reference/test_parameter_source_figures.py::test_katohs_mac_equations_at_age_40_give_the_figures_printed, tests/reference/test_parameter_source_figures.py::test_yasudas_brain_column_recovers_the_blood_gas_coefficients_printed
---

**Problem.** These `docs/MODEL.md` sections state figures with a unit in
paragraphs that carry no test, marker, source or date. Counted 2026-11-02
with `_numeric_paragraph_members`, as unheld of numeric paragraphs:

- "Supported input ranges": 6 of 29
- "Delivery-limit and MAC parameters": 5 of 8
- "Source hierarchy: what may be cited as the authority for a value": 4 of 38
- "v0.2.0: isoflurane and desflurane": 1 of 3

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

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present in part when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. It stays deferred to the next gate: its `deferred-from:` records the check that no learner can see a wrong value now (`PL-8C8W`). 15 of the 16 unheld paragraphs were in `docs/MODEL.md` at `817a4d88`. The 16th, "What is not bounded this way", gained its figure with `879623a3` (2026-10-26).

**Checked 2026-11-22** against `d4e8200`: still applies, and more is unheld than the brief counts. A recount on 2026-11-22 with `_numeric_paragraph_members` finds: "Supported input ranges" 13 of 25, "Delivery-limit and MAC parameters" 6 of 7, "Source hierarchy: what may be cited as the authority for a value" 28 of 39, and "v0.2.0: isoflurane and desflurane" 4 of 5. None is in `BOUND_FAMILIES`. Two section homes have changed. "Supported input ranges" is now in `docs/INTERFACE.md` (moved by #2109, `PL-CTXZ`). The other three sit under § "Parameter provenance", which `PL-FWR6` moved to `docs/PARAMETERS.md`. So point this pass's families at that document.

**Closed 2026-11-22.** The four sections are in `BOUND_FAMILIES` with `_numeric_paragraph_members`: `docs/INTERFACE.md` § "Supported input ranges" and, in `docs/PARAMETERS.md`, § "Source hierarchy: what may be cited as the authority for a value", § "v0.2.0: isoflurane and desflurane" and § "Delivery-limit and MAC parameters". Every numeric paragraph in them names a test that computes its figures or cites its source.

Two new files hold the new tests. `tests/reference/test_supported_input_range_figures.py` computes $`F_A/F_I`$ at five minutes at five cardiac outputs, the MAC-hours a long sevoflurane run reaches, and the run length as a fraction of sevoflurane's fat time constant. `tests/reference/test_parameter_source_figures.py` computes the stored blood:gas coefficients' gaps from the measured ones, the stored tissue coefficients' distance from Yasuda's means, the vessel-rich comparison with Yasuda's brain values, the time-constant changes that storing Yasuda's means would make, the desflurane MAC-awake arithmetic, and Katoh's MAC equations at age 40. Each test fails when its printed figure is changed.

Sources read on PubMed on 2026-11-22, index record and abstract only: Kharasch 1995 (PMID 7486145), Strum and Eger 1987 (PMID 3605675), Lerman et al. 1984 (PMID 6465597), Eger 1987 (PMID 3631593), Esper et al. 2015 (PMID 25393590), Yasuda, Targ and Eger 1989 (PMID 2774233), Mapleson 1996 (PMID 8777094), Katoh et al. 1993 (PMID 8214700), Chortkoff et al. 1995 (PMID 7574003) and Rampil et al. 1991 (PMID 2001020). The figures from the body of Katoh's paper (cerebral blood flow 14.3% of cardiac output, 21 mL/kg of brain, and the coefficients it used) and Mapleson's confidence limits are held by the citation only. Lerman et al., Eger and Esper et al. are cited only in the new blood:gas test, for the measured means it compares with.

Computed claims found wrong or missing a condition: three.

1. `docs/INTERFACE.md` said that Kharasch's review "measured how sevoflurane's metabolism scales with dose only from 0.35 to 9.5 MAC-hours". The abstract gives that range as the doses in the studies of plasma fluoride that the review summarizes. The sentence now says so in `docs/INTERFACE.md`, in `docs/MODEL.md` § "Known limitations" (which had "Kharasch's review covers 0.35 to 9.5 MAC-hours") and in the comment in `core/supported_ranges.py` (`PL-0VZ5`). The blind review caught a first rewording that still overstated it.
2. `docs/PARAMETERS.md` § "v0.2.0" said that Table 1 ÷ Table 2 recovers blood:gas values 4.9–9.4% above the stored ones. The brain column, which the abstract gives, recovers values 4.1% and 2.4% above and 0.3% below, which a new test now computes (`test_yasudas_brain_column_recovers_the_blood_gas_coefficients_printed`). The paragraph now gives those, and `PL-S5JJ` holds the other tissues and the same sentence in the agent files.
3. `docs/INTERFACE.md` § "The washout tail inside the limit" said the tail runs "a fifth to a half above" the curves before the middle stretch. `docs/VERIFICATION.md` and the recorded ratios give 12 to 52% at the widest, and desflurane's excess is about 11%. The sentence now gives 12 to 52%.

One sentence of `docs/INTERFACE.md` restated an open-circuit figure from `docs/VERIFICATION.md` that no test computes. It was removed there, since the paragraph already points to that subsection.

Blind review, two passes. Pass 1: the cited-only 4.9–9.4% range (should-fix, fixed), the early-excess figure and the overclaim that two tests check the paragraph (should-fix, fixed), and the Kharasch rewording still overstating its source (optional, fixed). Pass 2: the Kharasch rewording (should-fix, fixed, repeat), the 4.9–9.4% range (should-fix, fixed, repeat), and `PL-0VZ5` left open (optional, already closed on the branch when the review ran on an earlier commit).

Files checked in the sweep: `docs/INTERFACE.md`, `docs/PARAMETERS.md`, `docs/MODEL.md`, `docs/VERIFICATION.md`, `README.md` and `src/anesthesia_sim/core/supported_ranges.py`, for the Kharasch sentence and the figures the new tests compute.
