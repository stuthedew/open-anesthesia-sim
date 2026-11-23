---
id: PL-MCQ5
title: Hold the numeric paragraphs in docs/MODEL.md's required-test sections (published wash-in and elimination, independent solution) to named tests
priority: P1
effort: M
status: done
classes: docs, science
feature: model-claims-held-by-tests
milestone: v0.6.22
touches: docs/MODEL.md, tools/doc_check.py, tests, docs/items
blocked-by: PL-19W8
deferred-from: v0.7.0 - not live: checked 2026-11-07 (PL-8C8W): the paragraphs it would hold are docs/MODEL.md prose that no displayed string carries, so no learner can see a wrong value now
added: 2026-11-02
closed: 2026-11-22
pr: 2263
payoff: the numbers in the required-test sections of docs/MODEL.md are computed by a named test, so a wrong one fails the build rather than waiting for a reader
tests: tests/reference/test_independent_solution_figures.py::test_each_run_is_at_most_0_8_times_as_exposed_to_rounding_as_at_the_earlier_step, tests/reference/test_independent_solution_figures.py::test_the_envelope_corner_and_the_held_hour_count_the_rounding_printed, tests/reference/test_independent_solution_figures.py::test_each_run_at_the_envelope_corner_has_the_derived_bound_printed, tests/reference/test_independent_solution_figures.py::test_the_random_runs_move_every_1_to_20_s_and_reach_each_zero_setting, tests/reference/test_published_wash_in_figures.py::test_the_rebreathing_circuit_returns_about_three_tenths_of_the_alveolar_fraction, tests/reference/test_published_wash_in_figures.py::test_the_alveolar_fraction_at_discontinuation_at_the_1_percent_dial_is_as_printed, tests/reference/test_published_wash_in_figures.py::test_the_vessel_rich_group_s_time_constant_is_2_0_to_2_7_minutes, tests/reference/test_published_wash_in_figures.py::test_the_stored_vessel_rich_coefficients_lie_within_3_percent_of_yasudas_brain_values, tests/reference/test_published_wash_in_figures.py::test_normalising_the_fitted_amplitudes_would_move_the_curves_by_the_percentages_printed, tests/reference/test_published_wash_in_figures.py::test_the_fourth_term_is_4_to_5_percent_of_the_fitted_curve_at_five_minutes, tests/reference/test_published_wash_in_figures.py::test_the_published_amplitude_spreads_are_the_shares_of_their_means_printed, tests/reference/test_published_wash_in_figures.py::test_the_model_s_apparent_terms_against_the_fitted_ones_give_the_ratios_printed, tests/reference/test_published_wash_in_figures.py::test_the_open_circuit_tail_s_lowest_points_are_as_printed, tests/reference/test_published_wash_in_figures.py::test_the_shipped_tail_s_first_dip_is_15_to_44_percent_below_the_fitted_curve, tests/reference/test_published_wash_in_figures.py::test_the_shipped_readout_shows_below_its_resolution_from_the_hours_printed, tests/reference/test_published_wash_in_figures.py::test_the_open_circuit_tail_first_falls_below_the_fitted_curve_in_the_minutes_printed, tests/reference/test_published_wash_in_figures.py::test_the_early_wash_in_points_past_one_sd_and_at_12_5_and_15_minutes_are_as_printed, tests/reference/test_published_wash_in_figures.py::test_the_wash_in_keeps_the_published_order_at_each_swept_flow
---

**Problem.** These `docs/MODEL.md` sections state figures with a unit in
paragraphs that carry no test, marker, source or date. Counted 2026-11-02
with `_numeric_paragraph_members`, as unheld of numeric paragraphs:

- "Published wash-in and elimination validation test": 13 of 50
- "Independent-solution test": 2 of 16

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

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present in part when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. It stays deferred to the next gate: its `deferred-from:` records the check that no learner can see a wrong value now (`PL-8C8W`). The unheld wash-in paragraphs and "The residual is rounding, not truncation" were in `docs/MODEL.md` at `817a4d88`. The nine-of-fifteen sentence came with `4d0def88` (2026-10-25 21:47), replacing a paragraph that was also unheld.

**Checked 2026-11-22** against `d4e8200`: still applies, and more is unheld than the brief counts. A recount on 2026-11-22 with `_numeric_paragraph_members` finds "Published wash-in and elimination validation test" 37 of 55 and "Independent-solution test" 9 of 20. Neither is a numeric family in `BOUND_FAMILIES`. Both sit under `docs/VERIFICATION.md` § "Required tests", which `PL-6PPZ` (claimed elsewhere) moves to a new verification document. So build this pass after that move.

**Closed 2026-11-22.** Both sections are in `BOUND_FAMILIES` with `_numeric_paragraph_members`: `docs/VERIFICATION.md` § "Independent-solution test" (0 of 28 numeric paragraphs unheld) and § "Published wash-in and elimination validation test" (0 of 54). Every numeric paragraph names a test that computes its figures, cites its source by PubMed id or journal locator, or dates the run that produced it.

Two new files hold the new tests. `tests/reference/test_independent_solution_figures.py` counts the rounding of each run as `run_rounding` does, at the one-second step and at the earlier 0.1 s step, and checks the 0.8 ratio, the 4 800/6 000 and 14 400/36 000 counts, the derived bound of 1.1e-11 for each of the three corner runs, and what the section says about the random runs. `tests/reference/test_published_wash_in_figures.py` computes the circuit's return of about three tenths of the alveolar fraction, the alveolar fraction at discontinuation, the vessel-rich time constants and coefficients, the effect of normalising the fitted amplitudes, the fourth term's share at five minutes, the amplitude spreads, the apparent-term ratios, the open-circuit tail's lowest points, the shipped tail's first dip and the hours at which the shipped trace falls below the readout's resolution. Each test reads its figures from the section as printed, so an edit that changes a figure fails as surely as a model change that moves one. That follows rule 9 of Sandve et al., "Ten simple rules for reproducible computational research", *PLoS Comput Biol* 2013;9:e1003285 (PMID 24204232, full text read 2026-11-22 via PMC3812051): connect each textual statement to the result that produced it.

Sources read on PubMed on 2026-11-22, index record and abstract only: Yasuda et al. 1991 (PMID 1994760 and PMID 2001028), Carpenter and Eger 1989 (PMID 2930000), Eger 1987 (PMID 3631593) and Esper et al. 2015 (PMID 25393590). The page numbers cited for Yasuda's papers come from the extraction notes in `docs/references/`.

Computed claims found wrong or missing a condition: six.

1. The derived bound was given as 1.1 to 1.6×10⁻¹¹. The unperfused load counts the same 4 800 units of rounding as the other two corner runs, because its zero-perfusion phase needs one squaring fewer, so all three bounds are 1.1×10⁻¹¹. The comment in `tests/reference/test_coupled_dynamics.py` said the same and is corrected.
2. Ordinary use's largest difference was given as 2.07e-15, from before MAC at age 40 (#2223) changed each agent's 1 MAC setting. It is now 2.19e-15, and the spread of the five runs a factor of 6.6, not 6.9.
3. The fourth compartment's term at five minutes was "about one part in twenty" of what remains. It is 4 to 5%, and sevoflurane's is about one part in 27. Corrected in `docs/VERIFICATION.md`, `docs/MODEL.md` and the docstring of `tests/reference/test_published_wash_in_and_elimination.py`.
4. The hours at which the alveolar readout stops showing a number were given as 2.8, 4.2 and 1.9 hours at a 1% dial, and "about the fifth hour" at a 6% desflurane dial. Those are roughly when the value falls below 0.01%. The readout, drawn by `format_percent`, shows `0.01%` until the value would round to 0.00%, and only then `<0.01%`. That happens at 4.9, 6.6 and 3.1 hours, and at about 7.8 hours for the 6% dial. Each is still before, or for the 6% dial inside, the stretch over which the trace runs below the measured mean, so the conclusion stands. My first correction gave 5.4 hours, and the second review pass found the threshold error. Corrected in `docs/VERIFICATION.md`, `docs/MODEL.md` and the docstring of `tests/reference/test_late_washout_against_published_fits.py`.
5. The wash-in comparison was said to hold "at every fresh gas flow from 1 to 10 L/min". It runs at six flows: 1, 2, 4, 6, 8 and 10 L/min. Corrected in three places in `docs/VERIFICATION.md`, two in `docs/MODEL.md`, and four docstrings in `tests/reference/test_published_wash_in_and_elimination.py` and `tests/reference/test_late_washout_against_published_fits.py`. One of those, for the open-circuit flow sweep, said "the whole supported flow range including zero" of a sweep at seven flows. `docs/MODEL.md` also said the solubility ordering holds at each of those flows, which the gate checks only at 10 L/min. A new test, `test_the_wash_in_keeps_the_published_order_at_each_swept_flow`, now checks it at all six, and it holds.
6. The 12.5- and 15-minute points were said to sit at +0.75 to +0.95 SD. The second isoflurane study's 12.5-minute point sits at +1.06 SD, under its regression band. Corrected in `docs/VERIFICATION.md` and the docstring of `tests/reference/test_published_wash_in_and_elimination.py`.

**Generator check.** The cause of claims 1, 2 and 4 is a figure computed once by hand and written into prose that no test computed, so a later model change or a miscount left it wrong. That is the cause this feature exists to remove, and these two sections now fail the build when a figure is unheld. Claims 3, 5 and 6 are roundings or omissions of the same kind. No new generator.

Files checked in the sweep: `docs/VERIFICATION.md`, `docs/MODEL.md`, `docs/INTERFACE.md`, `docs/PARAMETERS.md`, `README.md`, `src/` and `tests/`, by searching for each corrected figure's old wording ("fifth hour", "one part in twenty", "every fresh gas flow from 1", "0.95 SD", "2.07", "1.6×10⁻¹¹" and "factor of 6.9"). The 2.07 in `docs/MODEL.md` and `docs/PARAMETERS.md` is the fat group's blood flow in mL per 100 mL per minute, a different figure.

Blind review, two passes. Pass 1: the +1.06 SD and +0.75 to +0.95 SD figures cited a test that checks only the regression band (should-fix, fixed with `test_the_early_wash_in_points_past_one_sd_and_at_12_5_and_15_minutes_are_as_printed`), the open circuit's first crossing in minutes cited a test that checks crossings only to a tenth of an hour (optional, fixed with `test_the_open_circuit_tail_first_falls_below_the_fitted_curve_in_the_minutes_printed`), the vessel-rich test ignored the printed Yasuda values (optional, fixed), and four docstrings kept the flow over-claim (optional, fixed). Pass 2: the readout hours used the wrong threshold (should-fix, fixed, claim 4 above), and the ordering was claimed at six flows but checked at one (optional, fixed).
