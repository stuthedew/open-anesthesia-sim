---
id: PL-7M65
title: tests/reference/test_mac_awake_washout_figures.py does not read the vessel-rich '0.84 MAC' figure, although docs/INTERFACE.md says the test checks each figure of the washout protocol
priority: P3
effort: S
status: done
classes: defect
feature: interface-matches-its-spec
milestone: v0.6.19
touches: tests/reference/test_mac_awake_washout_figures.py, tests/reference/test_coupled_dynamics.py, tests/reference/test_canonical_evaluation.py
added: 2026-11-21
closed: 2026-11-21
pr: 2201
payoff: The vessel-rich figure that docs/INTERFACE.md teaches for the washout is checked against the model, so a parameter change cannot leave it wrong
tests: tests/reference/test_mac_awake_washout_figures.py::test_the_mac_awake_washout_figures_match_the_model
---

**Problem.** tests/reference/test_mac_awake_washout_figures.py does not read the vessel-rich '0.84 MAC' figure, although docs/INTERFACE.md says the test checks each figure of the washout protocol

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/INTERFACE.md` § "MAC-awake as a chart reference" says of its washout protocol "An automated test reruns this protocol and checks each figure to the decimal places printed here." One figure is not read: "In the 3-hour run above, the vessel-rich trace reached only 0.84 MAC, as the alveolar trace did." `_printed` in `tests/reference/test_mac_awake_washout_figures.py` reads a maintenance value only through the pattern for "alveolar fraction only to N%, or N MAC", `Washout` has no vessel-rich maintenance field, and `FIGURES` has nine entries, none for it.

The figure is true today: the vessel-rich trace stands at 0.8426 MAC at 3 hours. Reproduction: copy the document, change that sentence to "reached only 0.99 MAC", point the test module's `INTERFACE_PATH` at the copy and call `_printed()`. The returned `PrintedFigures` holds `maintenance_alveolar_mac='0.84'` and no field with 0.99, so every comparison still passes.

**Why it matters.** A change to the vessel-rich group's coefficient or volume, or an edit to that figure, would leave a wrong number on the page with the test green.

**Done when.** The test reads the vessel-rich figure from the section and compares it with the rerun, and an edit of that figure in a copy of the document fails it.

**Closed 2026-11-21.** The test now reads "the vessel-rich trace reached only 0.84 MAC" from `docs/INTERFACE.md` § "MAC-awake as a chart reference", computes the vessel-rich fraction at the end of the three-hour maintenance, divides it by the agent's MAC, and compares the two at the printed precision. The model gives 0.8426. With the printed figure edited to 0.99 in a copy of the document, the test failed with "assert '0.84' == '0.99'". Three reference-test docstrings that `PL-PH3N` found stale ride here, because an edit under `tests/reference/` waits for the owner's read: the module docstring of this test named `docs/MODEL.md` and "six figures"; `test_coupled_dynamics.py` gave rounding margins measured on an older model (re-measured 2026-11-21: 8e-9 counts, a widest differential of 2.06e-14 in fraction, and a smallest true gap of 1.12e-15); and `test_canonical_evaluation.py` said the accumulators are shown to six decimals of a litre, where the accounting View shows run totals to 0.1 L (`_RUN_TOTAL_LITRE_DECIMALS`). Documents checked: `docs/INTERFACE.md` § "MAC-awake as a chart reference", which names this test as checking each figure and now does, and `docs/ARCHITECTURE.md` § "Tests (`tests/`)", which describes the reference tree and does not change.

**Blind review 2026-11-21.** One pass found two things, both acted on: the coupled-dynamics comment said `docs/MODEL.md` quotes the pairwise measurement, where `docs/INTERFACE.md` does, and a second docstring in `test_canonical_evaluation.py` still compared a divergence with a 1e-6 L resolution that no View uses. Both are fixed here. The first also found that `docs/INTERFACE.md` still gives the older pairwise figures, filed as `PL-VM4Q`.

**Bounds only, 2026-11-22.** The owner answered the question on #2201 with "Whatever best practice is. Look it up". The comments in `test_coupled_dynamics.py` and `test_canonical_evaluation.py` that this item touched now state each bound and the reason for it, and quote no measured margin that no test asserts. Sources read 2026-11-22: Wilson et al., "Best Practices for Scientific Computing", PLoS Biol 2014;12(1):e1001745 (https://pmc.ncbi.nlm.nih.gov/articles/PMC3886731, full text through section 7), practice 5a, which says assertions are "executable documentation" and more useful than comments "since the reader can be sure that they are accurate and up to date", and practice 7a, "Document interfaces and reasons, not implementations"; and PEP 8 § "Comments" (https://peps.python.org/pep-0008/): "Comments that contradict the code are worse than no comments." This agrees with the owner's rule of 2026-11-14 (`PL-GJ1W`). The re-measured figures stay in the paragraph above, which is their record. The two figures that had gone stale in these comments, 1.104e-12 and the 1e-6 L resolution, are the evidence for the rule. The other measured margins in these files predate this item and are filed separately.

**Generator check.** One-off. The fact misread is which figures of the washout section the test reads: the figure was added to `docs/INTERFACE.md` without a matching pattern in `_printed`, and nothing compares the figures the section prints with the ones the test extracts.

**Checked 2026-11-22, merging main into `PL-Z6C8`:** `PL-Z6C8` deletes `tests/reference/test_canonical_evaluation.py` with the evaluation paths it tested, so the two docstrings this item corrected there go with it. The merge keeps this item's bounds-only wording in `tests/reference/test_coupled_dynamics.py`, with the count of pair comparisons at the one-second step, 148 500, which `docs/INTERFACE.md` already quotes. It drops the sentence that crossings are sampled at gaps below the pairwise differential, because at the one-second step none is sampled that closely.
<!-- absent: tests/reference/test_canonical_evaluation.py -->
