---
id: PL-SP6H
title: Check two docs/MODEL.md agent-amount precision claims against the figures they cite: 0.1 L is said to lie between a quarter of an SD and six SDs, but the quoted 0.016-0.23 L shifts give about 0.43 SD at the coarse end; and 0.1 mL of delivered liquid is said to lie inside the density's band, though at 8% and 10 L/min over 24 h one step is about a thirtieth of an SD
priority: P1
effort: S
status: needs-decision
classes: defect, safety
feature: model-claims-held-by-tests
touches: docs/MODEL.md, src/anesthesia_sim/app/formatting.py, tests/unit/test_formatting.py
added: 2026-11-04
payoff: every precision the agent-amount totals show is backed by arithmetic that matches the figures it cites, and none shows a last digit finer than its uncertainty supports
---

**Problem.** Check two docs/MODEL.md agent-amount precision claims against the figures they cite: 0.1 L is said to lie between a quarter of an SD and six SDs, but the quoted 0.016-0.23 L shifts give about 0.43 SD at the coarse end; and 0.1 mL of delivered liquid is said to lie inside the density's band, though at 8% and 10 L/min over 24 h one step is about a thirtieth of an SD

**Checked 2026-11-04**, by hand from the figures that `docs/MODEL.md` § "Displayed precision" gives. No test computes any of them.

1. "One count of 0.1 L therefore lies between a quarter of an SD and six SDs." The quoted shifts run from 0.016 L to 0.23 L, so 0.1 L is about 0.43 SD where the shift is largest and 6.3 SD where it is smallest. The low end is about two-fifths of an SD, not a quarter. The conclusion holds, because two-fifths is coarser than the readouts' seventh of an SD.
2. Not in the capture: "A count of 0.01 L would fall to a fiftieth of an SD by 24 h." Against shifts of 0.18 to 0.23 L, 0.01 L is an eighteenth to a twenty-third of an SD, about a twentieth. The compartment-amount paragraph repeats "the totals' second decimal at a fiftieth". The refusal of 0.01 L still holds, because a twentieth is finer than a seventh.
3. "So 0.1 mL lies inside the band that the density spans across the supported settings." At 8% sevoflurane and 10 L/min for 24 h, the delivered total is 1,152 L of vapour, about 6,300 mL of liquid at the section's 0.55 mL per 0.1 L. The paragraph says one SD of the density moves the figure by 0.1 mL at 190 mL, so it moves it by about 3.3 mL at 6,300 mL, and 0.1 mL is about a thirtieth of an SD. The step becomes finer than a seventh of an SD, the finest the section admits for the readouts, once a run has delivered about 1,300 mL of sevoflurane liquid. That takes about 5 h at 8% and 10 L/min, and more than 24 h at 2% and 2 L/min. This conclusion does not hold across the supported span.

The first two sentences date from `6ce8e6991` (`PL-BZR4`, 2026-10-25) and the third from `2330f33f6` (`PL-0S0V`, 2026-10-26).

**Why it matters.** `docs/MODEL.md` is the specification that justifies each displayed precision. The first two are wrong figures under correct conclusions. The third is a precision the section's own rule refuses: in long high-flow runs, the delivered total in millilitres of liquid shows a last digit finer than its uncertainty supports, which is the false precision the safety-critical standard forbids. The 2026-10-27 decision to show 0.1 mL rather than whole millilitres rested on that sentence.

**Decision needed.** Which resolution should the delivered total in millilitres of liquid take, now that 0.1 mL is finer than the derivation admits beyond about 1,300 mL of sevoflurane liquid? The answer changes what a learner sees and reopens a ratified decision on a measurement, so it is the owner's.

- **A. Keep 0.1 mL**, and say in the paragraph that the last digit is finer than a seventh of an SD beyond about 1,300 mL of liquid. The learner sees no change. The section then carries an exception to the rule it uses to refuse 0.01 L, and `AgentAmountPrecision` no longer holds the finest count the derivation supports for this entry.
- **B. Whole millilitres**, the option the 2026-10-27 decision was chosen over. At 8% sevoflurane and 10 L/min for 24 h, 1 mL is about 0.3 SD, so it is never finer than the band. The delivered and exhausted totals then read at one scale in one unit, as the section asks of the litre display. A 30-minute case at 2% and 2 L/min shows 7 mL instead of 6.6 mL, and the cost a reader computes from it can be off by up to half a millilitre's price.
- **C. Four significant figures**, as the compartment amounts use significant figures, since the density's uncertainty is a fixed share of the amount. The step stays between about a fifth of an SD and four SDs everywhere. It adds a second display rule for one total, and the delivered and exhausted totals no longer share a scale.

**Recommendation: B, whole millilitres.** It is the only option that stays inside the derivation's band across the whole supported span with no exception, and it matches the exhausted total in the same unit. It gives up at most half a millilitre's price on the cost. The decision it reverses was taken on the sentence this check found false.

**Done when.** The two litre figures read about two-fifths of an SD and about a twentieth, in the litre paragraph and in the compartment-amount paragraph. The delivered total in millilitres of liquid takes the resolution the owner chose, and its paragraph states where that resolution lies against the band. The comment beside `AGENT_AMOUNT_DISPLAY_PRECISION` in `src/anesthesia_sim/app/formatting.py`, which restates the same derivation, agrees with the paragraph. `test_agent_amounts_precision` pins the chosen count.

**Generator check.** Stock of `PL-B6YV`'s fact, whether a `docs/MODEL.md` sentence about what the model computes matches what it computes. All three sentences were written before that head closed on 2026-11-02, so this is not a re-entry. The litre shifts carry the declared gap to `PL-19W8`, which counts the claims found wrong in this section and should count these three.
