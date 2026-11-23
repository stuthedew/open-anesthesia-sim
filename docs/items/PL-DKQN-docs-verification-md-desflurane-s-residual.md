---
id: PL-DKQN
title: docs/VERIFICATION.md § "Desflurane's residual" compares the model's tissue:blood ratios, which divide by the stored blood:gas coefficients, with Yasuda 1989's brain:blood ratios, which divide by age-adjusted published ones, so its SD distances and its 3% agreement mix two denominators (blind review of PL-XGLH, 2026-11-23)
priority: P1
effort: M
status: ready
classes: defect, science
feature: provenance
touches: docs/VERIFICATION.md, tests/reference/test_published_wash_in_figures.py, tests/reference/test_published_wash_in_and_elimination.py, src/anesthesia_sim/data/agents/desflurane.json
deferred-from: v0.7.0 - not live: no stored or displayed value is computed from the comparison, and desflurane's conclusion holds on either denominator
added: 2026-11-23
filed-pr: 2313
payoff: a developer checking why desflurane's vessel-rich coefficient was not raised finds distances that reproduce from the paper's measured values
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
