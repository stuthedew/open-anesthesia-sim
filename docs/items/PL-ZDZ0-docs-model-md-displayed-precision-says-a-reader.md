---
id: PL-ZDZ0
title: docs/MODEL.md § Displayed precision says a reader can never watch the MAC digit move while the percent digit stays still, but the two readouts round at different boundaries: sevoflurane at 0.029% and 0.031% both read 0.03% while MAC reads 0.01 then 0.02
priority: P1
effort: S
status: ready
classes: defect, safety
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tests/unit/test_formatting.py
deferred-from: v0.7.0 - captured after the freeze; every displayed value is correct, and the false sentence is in docs/MODEL.md rather than on screen
added: 2026-11-03
payoff: a clinician reading docs/MODEL.md is no longer told a MAC readout cannot change on its own, so a rounding step is not mistaken for a real change the percent readout hides
verify: ! grep -qF 'must never be able to watch the MAC digit' docs/MODEL.md && grep -q 'def test_the_mac_digit_can_move_alone_at_a_rounding_boundary' tests/unit/test_formatting.py
---

**Problem.** `docs/MODEL.md` § "Displayed precision" says: "A reader must never be able to watch the MAC digit move while the percent digit stays still." The displayed values are right, but this claim is false, because the two readouts round at boundaries that do not line up. Measured 2026-11-03 with `format_percent` and `format_mac_multiple` from `src/anesthesia_sim/app/formatting.py`, at a MAC of 2.0%: 0.029% reads `0.03%` and `0.01 ×MAC`, and 0.031% reads `0.03%` and `0.02 ×MAC`. A reader who trusts the sentence could take a moving MAC digit as a real change the percent readout hides.

**Found by.** The prose review on `PL-XQXK` (#1976), close-out step 8.

**What does hold.** One step of the MAC readout (0.01 MAC) is coarser than one step of the percent readout (0.01 percentage points) for every shipped agent, so over a full step the MAC figure never resolves a finer difference than the percent figure. `test_the_mac_resolution_is_derived_from_the_percent_resolution` checks that step comparison and nothing about rounding boundaries.

**Reproduced 2026-11-03.** The same two calls, with `MacPercent(2.0)`, return `0.03%` and `0.01 ×MAC` for 0.029%, and `0.03%` and `0.02 ×MAC` for 0.031%. The false sentence is still in § "Displayed precision", in the paragraph that begins "One count of the MAC line".

**Why it matters.** `docs/MODEL.md` is what a clinician reads to decide what a displayed value means. This sentence tells them that a MAC readout changing on its own cannot happen. When it does happen, near a rounding boundary, a reader who trusts the document could take it as a real change in the patient that the percent readout is hiding.

**Done when.** The paragraph no longer says the MAC digit can never move alone. It states the claim that holds: one step of the MAC readout is coarser than one step of the percent readout for every shipped agent. It also says that near a rounding boundary the MAC digit can change while the percent digit does not. A test in `tests/unit/test_formatting.py` named `test_the_mac_digit_can_move_alone_at_a_rounding_boundary` pins the 0.029% and 0.031% sevoflurane example, and the paragraph names it. Because the sentence says what a displayed clinical value means, the rewrite goes to the owner's read before it merges.

This was decided at triage, over the brief's earlier "either a test or a sentence": the reader needs the sentence, and the test is what holds the sentence to the code.

**Generator check.** One-off: one sentence that was never true, found by a prose review; the feature model-claims-held-by-tests is the mechanism for it.
