---
id: PL-7M65
title: tests/reference/test_mac_awake_washout_figures.py does not read the vessel-rich '0.84 MAC' figure, although docs/INTERFACE.md says the test checks each figure of the washout protocol
status: untriaged
feature: interface-matches-its-spec
added: 2026-11-21
---

**Problem.** tests/reference/test_mac_awake_washout_figures.py does not read the vessel-rich '0.84 MAC' figure, although docs/INTERFACE.md says the test checks each figure of the washout protocol

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/INTERFACE.md` § "MAC-awake as a chart reference" says of its washout protocol "An automated test reruns this protocol and checks each figure to the decimal places printed here." One figure is not read: "In the 3-hour run above, the vessel-rich trace reached only 0.84 MAC, as the alveolar trace did." `_printed` in `tests/reference/test_mac_awake_washout_figures.py` reads a maintenance value only through the pattern for "alveolar fraction only to N%, or N MAC", `Washout` has no vessel-rich maintenance field, and `FIGURES` has nine entries, none for it.

The figure is true today: the vessel-rich trace stands at 0.8426 MAC at 3 hours. Reproduction: copy the document, change that sentence to "reached only 0.99 MAC", point the test module's `INTERFACE_PATH` at the copy and call `_printed()`. The returned `PrintedFigures` holds `maintenance_alveolar_mac='0.84'` and no field with 0.99, so every comparison still passes.

**Why it matters.** A change to the vessel-rich group's coefficient or volume, or an edit to that figure, would leave a wrong number on the page with the test green.

**Done when.** The test reads the vessel-rich figure from the section and compares it with the rerun, and an edit of that figure in a copy of the document fails it.

**Closed 2026-11-21.** The test now reads "the vessel-rich trace reached only 0.84 MAC" from `docs/INTERFACE.md` § "MAC-awake as a chart reference", computes the vessel-rich fraction at the end of the three-hour maintenance, divides it by the agent's MAC, and compares the two at the printed precision. The model gives 0.8426. With the printed figure edited to 0.99 in a copy of the document, the test failed with "assert '0.84' == '0.99'". Three reference-test docstrings that `PL-PH3N` found stale ride here, because an edit under `tests/reference/` waits for the owner's read: the module docstring of this test named `docs/MODEL.md` and "six figures"; `test_coupled_dynamics.py` gave rounding margins measured on an older model (re-measured 2026-11-21: 8e-9 counts, a widest differential of 2.06e-14 in fraction, and a smallest true gap of 1.12e-15); and `test_canonical_evaluation.py` said the accumulators are shown to six decimals of a litre, where the accounting View shows run totals to 0.1 L (`_RUN_TOTAL_LITRE_DECIMALS`). Documents checked: `docs/INTERFACE.md` § "MAC-awake as a chart reference", which names this test as checking each figure and now does, and `docs/ARCHITECTURE.md` § "Tests (`tests/`)", which describes the reference tree and does not change.
