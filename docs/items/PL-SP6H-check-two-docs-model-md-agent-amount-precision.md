---
id: PL-SP6H
title: Check two docs/MODEL.md agent-amount precision claims against the figures they cite: 0.1 L is said to lie between a quarter of an SD and six SDs, but the quoted 0.016-0.23 L shifts give about 0.43 SD at the coarse end; and 0.1 mL of delivered liquid is said to lie inside the density's band, though at 8% and 10 L/min over 24 h one step is about a thirtieth of an SD
priority: P1
effort: S
status: done
classes: defect, safety
feature: model-claims-held-by-tests
milestone: v0.6.17
touches: docs/MODEL.md, src/anesthesia_sim/app/formatting.py, tests/unit/test_formatting.py, tests/unit/test_agent_cost.py, tests/integration/test_agent_cost_view.py, ROADMAP.md
added: 2026-11-04
closed: 2026-11-04
pr: 2024
payoff: every precision the agent-amount totals show is backed by arithmetic that matches the figures it cites, and none shows a last digit finer than its uncertainty supports
verify: ! grep -qF 'is shown to a tenth' docs/MODEL.md && grep -qF 'def test_the_delivered_total_in_millilitres_of_liquid_is_shown_in_whole_millilitres' tests/unit/test_formatting.py
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

**Answered 2026-11-04** (project owner, 2026-11-04, ratified, over keeping 0.1 mL with a stated exception and over four significant figures): whole millilitres. The delivered total in millilitres of liquid steps in 1 mL, as the exhausted total does. This replaces the 2026-10-27 decision that `docs/MODEL.md` and the comment beside `AGENT_AMOUNT_DISPLAY_PRECISION` record.

[superseded 2026-11-04: the owner chose whole millilitres, and the decided form follows] **Done when.** The two litre figures read about two-fifths of an SD and about a twentieth, in the litre paragraph and in the compartment-amount paragraph. The delivered total in millilitres of liquid takes the resolution the owner chose, and its paragraph states where that resolution lies against the band. The comment beside `AGENT_AMOUNT_DISPLAY_PRECISION` in `src/anesthesia_sim/app/formatting.py`, which restates the same derivation, agrees with the paragraph. `test_agent_amounts_precision` pins the chosen count.

**Generator check.** Stock of `PL-B6YV`'s fact, whether a `docs/MODEL.md` sentence about what the model computes matches what it computes. All three sentences were written before that head closed on 2026-11-02, so this is not a re-entry. The litre shifts carry the declared gap to `PL-19W8`, which counts the claims found wrong in this section and should count these three.

**Done when** (2026-11-04, decided form). The two litre figures read about two-fifths of an SD and about a twentieth, in the litre paragraph and in the compartment-amount paragraph. `AGENT_AMOUNT_DISPLAY_PRECISION` gives the delivered total in millilitres of liquid no decimals, so the agent cost View shows it in whole millilitres, and the precision table in `docs/MODEL.md` reads 0 decimals and 1 mL for it. The paragraph on the delivered total in millilitres of liquid, and the comment beside the constant, give the new step's reason: at 8% sevoflurane and 10 L/min for 24 h, 1 mL is about 0.3 SD, so it is never finer than a seventh of an SD in the supported span. Both record this decision with its date and kind. The hazard row that promises a cost is shown beside the two numbers it multiplied is checked against the new step, and it says how a volume rounded to the millilitre relates to the cost beside it. `test_the_displayed_cost_reproduces_gas_man_s_printed_costs`, whose 39.4 mL of isoflurane now reads 39 mL, is checked against the new step too. `test_the_delivered_total_in_millilitres_of_liquid_is_shown_in_whole_millilitres` replaces the test that pins a tenth, and `test_agent_amounts_precision` pins the new count.

**Built 2026-11-04.** The agent cost View now shows the delivered total in millilitres of liquid in whole millilitres: 39.4 mL reads 39 mL, 0.0 mL reads 0 mL, and a positive amount below half a millilitre reads `<1 mL of liquid`. The work also changed two test files and `ROADMAP.md`, which the first `touches` line did not list. `tests/unit/test_agent_cost.py` and `tests/integration/test_agent_cost_view.py` pinned the tenth in the drawn text. The gate paragraph that admitted this item said, in the present tense, that the View shows 0.1 mL. The cost paragraph's worked example now shows that its two figures multiply to USD 7.98 beside a cost of USD 8.07, and the cost hazard row says why. `test_the_delivered_agent_is_shown_to_a_tenth_with_its_unit_named` is renamed `test_the_delivered_agent_is_shown_at_its_derived_precision_with_its_unit_named`, and the hazard row that cites it uses the new name.

**Regression test, run against the code before the fix.** `.venv/bin/python -m pytest -q tests/unit/test_formatting.py -k whole_millilitres` failed with `assert (1, 1) == (0, 0)` on the precision count, before `_FINEST_DERIVED_DECIMALS` gave the delivered liquid total 0 decimals. It passes after.

**Blind review, 2026-11-04.** Two passes on `#2024`.

- Pass 1, should-fix: at whole millilitres, two cost View tests could no longer tell one agent's vapour-to-liquid factor from another's, because desflurane's 2.86 mL and sevoflurane's 3.28 mL both drew 3 mL. Fixed: `test_patient_inputs_reach_the_drawn_liquid_figure_through_the_model` runs at 6 L/min, and the agent-change step of `test_the_panel_follows_its_run_through_an_agent_change_and_a_comparison` runs at 10 L/min. Each now asserts that the wrong agent's factor would draw a different figure.
- Pass 1, optional: early in a case the product of the two figures shown can be 30% from the cost, as when 1.43 mL of desflurane is shown as 1 mL. Rejected: the owner's case for whole millilitres stated the bound, half a millilitre's price, and that bound is largest relative to small totals. The readout says the figures are rounded and the cost is computed before rounding.
- Pass 2, should-fix: the litre paragraph's "across the whole supported span" claimed settings its shifts were never measured at. Fixed by narrowing the sentence to 1 MAC with the reference flows. The derivation at each agent's dial maximum is filed as `PL-0P3F` and admitted to v0.7.0's gate.
- Pass 2, optional: the cost paragraph judges its figures against one SD while the rest of the section uses a seventh. Filed as `PL-7R8S`, at `needs-decision` and deferred from the gate.
