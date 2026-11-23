---
id: PL-DKQN
title: docs/VERIFICATION.md § "Desflurane's residual" compares the model's tissue:blood ratios, which divide by the stored blood:gas coefficients, with Yasuda 1989's brain:blood ratios, which divide by age-adjusted published ones, so its SD distances and its 3% agreement mix two denominators (blind review of PL-XGLH, 2026-11-23)
priority: P1
effort: M
status: done
classes: defect, science
feature: provenance
touches: docs/VERIFICATION.md, tests/reference/test_published_wash_in_figures.py, tests/reference/test_published_wash_in_and_elimination.py, src/anesthesia_sim/data/agents/desflurane.json
deferred-from: v0.7.0 - not live: no stored or displayed value is computed from the comparison, and desflurane's conclusion holds on either denominator
added: 2026-11-23
closed: 2026-11-23
pr: 2315
filed-pr: 2313
payoff: a developer checking why desflurane's vessel-rich coefficient was not raised finds distances that reproduce from the paper's measured values
tests: tests/reference/test_published_wash_in_figures.py::test_the_stored_vessel_rich_coefficients_lie_within_1_sd_of_yasudas_brain_values, tests/reference/test_published_wash_in_figures.py::test_the_demanded_vessel_rich_coefficients_lie_from_yasudas_brain_values_as_printed
---

**Problem.** The table in `docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file was not changed" puts the model's demanded tissue:blood ratio beside Yasuda, Targ and Eger 1989's brain:blood ratio and gives the distance in the paper's SDs. The model's ratio divides a tissue:gas coefficient by the stored blood:gas coefficient (0.65, 1.30 and 0.42 for sevoflurane, isoflurane and desflurane). The paper's ratio divides its measured brain:gas coefficient (Table 1, p. 371) by an age-adjusted published blood:gas coefficient (p. 372), which Table 1 over Table 2 recovers as 0.676, 1.331 and 0.419. So the two columns have different denominators, and the column is headed "Measured" though the paper derived it.

**What the comparison gives on one denominator**, worked on 2026-11-23 from the paper's Table 1 brain row, read in the private corpus: I-653 (desflurane) 0.54 ± 0.02, sevoflurane 1.15 ± 0.07, isoflurane 2.09 ± 0.10. The demanded tissue:gas coefficient is the demanded ratio times the stored blood:gas coefficient.

| Agent | Demanded tissue:gas | Yasuda brain:gas | Distance | Distance now printed |
| --- | --- | --- | --- | --- |
| Sevoflurane | 1.74 × 0.65 = 1.131 | 1.15 ± 0.07 | −0.27 SD | +0.4 SD |
| Isoflurane | 1.45 × 1.30 = 1.885 | 2.09 ± 0.10 | −2.05 SD | −1.2 SD |
| Desflurane | 2.24 × 0.42 = 0.941 | 0.54 ± 0.02 | +20 SD | +19 SD |

Desflurane's conclusion does not change, because its two denominators differ by 0.2%. Isoflurane's does: at −2.05 SD, the sentence "Two of the three demanded values agree with that measurement" no longer holds as written. The same mix affects the sentence that the stored coefficients match the paper's brain:blood values "to within 3%", which `test_the_stored_vessel_rich_coefficients_lie_within_3_percent_of_yasudas_brain_values` in `tests/reference/test_published_wash_in_figures.py` holds. In tissue:gas, the stored vessel-rich values are 1.10, 2.1 and 0.54 against 1.15, 2.09 and 0.54, so sevoflurane's is 4.3% below the paper's mean (−0.71 SD), not 0.5%.

**Two stale reading-depth notes ride with it.** The docstring of `TissueSolubilityCeiling` in `tests/reference/test_published_wash_in_and_elimination.py` still says the brain:blood values "are read from the abstract" and were checked against PubMed on 2026-09-08, which `PL-XGLH` corrected beside the citation. The `sources` note in `src/anesthesia_sim/data/agents/desflurane.json` says the same, and also records the full-text reading of 2026-09-13 later in the note.

**Why it matters.** A developer who checks the table against the paper gets different distances, and the argument that only desflurane misses rests partly on isoflurane agreeing, which it does not on one denominator. No stored or displayed value is computed from the table.

**Approach, recommended.** Compare in tissue:gas, which is the quantity the paper measured and the quantity the model stores, so neither side carries a derived denominator. Rewrite the table and the two sentences from the numbers above, and change the 3% test to compare stored tissue:gas with Table 1's brain:gas means, choosing its bound from the paper's SDs rather than a percentage. A `tests/reference/` file that loses a line holds the pull request for an owner read, so the test change will need one.

**Done when.** The table and the sentences beside it compare one quantity on one denominator, the 3% test compares tissue:gas with Table 1, and the two reading-depth notes say the values were checked against the full text.

**Generator check.** A one-off. The table predates the note that `PL-XGLH` added, and the note is what made the two denominators visible.

**Checked 2026-11-23.** The same table was also copied into the docstring of `test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination` in `tests/reference/test_published_wash_in_and_elimination.py`, so that copy is in scope too.

**Done, 2026-11-23.** The table in `docs/VERIFICATION.md` § "Desflurane's residual" now gives each demanded tissue:blood ratio, the tissue:gas coefficient it implies at the stored blood:gas coefficient, Yasuda's measured brain:gas mean and SD, and the distance between them: −0.27 SD for sevoflurane, −2.05 SD for isoflurane and +20.04 SD for desflurane. The sentence beside it no longer says two of the three agree. It says isoflurane's demand lies just outside two SDs below its measurement, on the side opposite desflurane's, and that desflurane's is the only one above. The "within 3%" sentence now compares the stored vessel-rich tissue:gas coefficients with Yasuda's brain:gas means, within 1 SD, which the largest gap, sevoflurane's 0.71 SD, meets. The citation now quotes the brain:gas means beside the brain:blood ones and says why the table uses tissue:gas.

Two tests in `tests/reference/test_published_wash_in_figures.py` hold the numbers. `test_the_stored_vessel_rich_coefficients_lie_within_1_sd_of_yasudas_brain_values` replaces the 3% test. `test_the_demanded_vessel_rich_coefficients_lie_from_yasudas_brain_values_as_printed` is new and recomputes each row of the table. Both read Yasuda's means and SDs from the Yasuda table in `docs/PARAMETERS.md` § "Where the tissue:gas coefficients come from", through `_yasuda_table()`, so neither holds a copy. The docstring of `test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination` drops its copy of the table and points at the document and the new test. The `TissueSolubilityCeiling` docstring and the desflurane file's source note now say the brain:blood values were checked against the full text on 2026-11-23, and the note's sentence that sevoflurane and isoflurane "both land on" the measurement now gives the tissue:gas comparison.

Left as they were. The two ceilings in `DESFLURANE_TISSUE_SOLUBILITY_CEILINGS` are still tissue:blood ratios times the stored blood:gas coefficient. On one denominator desflurane's mean + 2 SD is 0.58 tissue:gas, against the 0.584 the test runs, so the ceiling moves by less than 1% and the test's conclusion does not depend on it. `docs/WORKING_NOTES.md`'s dated entry still says "nineteen standard deviations above ... brain:blood", which was true of the comparison it records.

Docs checked: `docs/VERIFICATION.md` § "Desflurane's residual" and § "Published wash-in and elimination validation test"; `docs/PARAMETERS.md` § "Where the tissue:gas coefficients come from" (unchanged, and now read by the tests); `docs/MODEL.md`'s derived tissue:blood row (unchanged, still true); `docs/references/yasuda-1989-tissue-solubility.md` (unchanged, still true); the source notes in `data/agents/sevoflurane.json` and `isoflurane.json` (dated history, unchanged).

Both new tests fail on `main`'s `docs/VERIFICATION.md`, checked 2026-11-23 by running them with that file restored: the 1 SD sentence is not there, and the table has no tissue:gas column, so no row matches.
