---
id: PL-ZDZ0
title: docs/MODEL.md § Displayed precision says a reader can never watch the MAC digit move while the percent digit stays still, but the two readouts round at different boundaries: sevoflurane at 0.029% and 0.031% both read 0.03% while MAC reads 0.01 then 0.02
status: untriaged
feature: model-claims-held-by-tests
added: 2026-11-03
---

**Problem.** `docs/MODEL.md` § "Displayed precision" says: "A reader must never be able to watch the MAC digit move while the percent digit stays still." The displayed values are right, but this claim is false, because the two readouts round at boundaries that do not line up. Measured 2026-11-03 with `format_percent` and `format_mac_multiple` from `src/anesthesia_sim/app/formatting.py`, at a MAC of 2.0%: 0.029% reads `0.03%` and `0.01 ×MAC`, and 0.031% reads `0.03%` and `0.02 ×MAC`. A reader who trusts the sentence could take a moving MAC digit as a real change the percent readout hides.

**Found by.** The prose review on `PL-XQXK` (#1976), close-out step 8.

**What does hold.** One step of the MAC readout (0.01 MAC) is coarser than one step of the percent readout (0.01 percentage points) for every shipped agent, so over a full step the MAC figure never resolves a finer difference than the percent figure. `test_the_mac_resolution_is_derived_from_the_percent_resolution` checks that step comparison and nothing about rounding boundaries.

**Done when.** The paragraph states the claim that holds, and either a test pins the weaker claim or the paragraph says the digit can move alone near a rounding boundary. Because the sentence says what a displayed clinical value means, the rewrite goes to the owner's read.
