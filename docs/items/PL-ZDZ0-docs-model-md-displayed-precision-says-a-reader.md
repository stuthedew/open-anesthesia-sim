---
id: PL-ZDZ0
title: docs/MODEL.md § Displayed precision says a reader can never watch the MAC digit move while the percent digit stays still, but the two readouts round at different boundaries: sevoflurane at 0.029% and 0.031% both read 0.03% while MAC reads 0.01 then 0.02
priority: P1
effort: S
status: done
classes: defect, safety
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tests/unit/test_formatting.py
deferred-from: v0.7.0 - captured after the freeze; every displayed value is correct, and the false sentence is in docs/MODEL.md rather than on screen
added: 2026-11-03
closed: 2026-11-03
pr: 1992
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

**Done 2026-11-03.** The paragraph in § "Displayed precision" now says the MAC readout's step is never smaller than the percent readout's, and a new paragraph after it says the MAC digit can move alone near a MAC rounding boundary, with the sevoflurane example and what a reader should take from it. The new test covers all three shipped agents with hand-worked expected strings (sevoflurane 0.029%/0.031%, isoflurane 0.017%/0.019%, desflurane 0.089%/0.091%), checks each stored MAC against the value the hand calculation used, and fails if an agent is added without a row. `test_no_mac_readout_claims_more_than_the_percent_beside_it` carried the same false claim in its docstring and was corrected too. The test pins behaviour the code already had, so it passes on the code before this change; there was no code defect for it to fail against. The new sentences say "step" for "count", as `PL-BSYT` asks; that item's rewrite of the rest of the paragraph is now unblocked.

**Blind review, 2026-11-03.** Pass 1 found that the first draft told a reader to treat a MAC digit moving alone as "a concentration sitting near a boundary, not as a change the percent readout is hiding". That was wrong. The model has no noise, so the MAC digit moves only when the modeled concentration really crossed a MAC boundary. Sevoflurane rising from 0.026% to 0.034% reads `0.03%` throughout while MAC goes from 0.01 to 0.02, a real rise of 0.008 percentage points that the percent readout does hide. The paragraph now says the change is real and smaller than one percent step, with no size beyond that bound. The "Why it matters" paragraph above carried the same wrong framing when the item was filed. Pass 2 found nothing.
