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

**Checked 2026-11-21:** `PL-PH3N` moved its entries 14 to 16 to this item. Entry 16 concerned `tests/reference/test_canonical_evaluation.py`, which `PL-Z6C8` deleted with the evaluation paths it tested, so only entries 14 and 15 remain.
<!-- absent: tests/reference/test_canonical_evaluation.py -->
