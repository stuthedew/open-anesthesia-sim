---
id: PL-SD5V
title: docs/MODEL.md states figures computed from the 20 °C reference temperature (the 5.8 % store bias, 5.5 % fewer moles, 24.055 L/mol, the 17 mL step) with no derived: marker naming REFERENCE_TEMPERATURE_CELSIUS, so changing the reference temperature leaves them stale with no refusal
priority: P1
effort: S
status: ready
classes: defect, safety
feature: model-claims-held-by-tests
touches: docs/MODEL.md, docs/INTERFACE.md
deferred-from: v0.7.0 - not live: checked 2026-11-22 at d4e8200c: REFERENCE_TEMPERATURE_CELSIUS is 20.0, and test_the_reference_condition_gap_is_the_ratio_of_molar_volumes computes the 5.8 % and 5.5 % from it, so every figure agrees with the constant and no learner can see a wrong value now
added: 2026-11-11
filed-pr: 2142
payoff: A change to the reference temperature can no longer leave the documents giving a clinician the wrong size for the liquid-conversion bias.
reenters: PL-5L84
---

**Problem.** docs/MODEL.md states figures computed from the 20 °C reference temperature (the 5.8 % store bias, 5.5 % fewer moles, 24.055 L/mol, the 17 mL step) with no derived: marker naming REFERENCE_TEMPERATURE_CELSIUS, so changing the reference temperature leaves them stale with no refusal

**Found by.** Blind review pass 1 on `PL-5L84` (#2142). The reviewer changed `REFERENCE_TEMPERATURE_CELSIUS` to 25 in a copy of the tree, and the documentation check then reported only the paragraphs that write "20 °C". The figures computed from it stayed silent: "reads 5.8% high" and the 17 mL step in § "Displayed precision" (the paragraph saying the stored total is refused in millilitres of liquid), "the 5.8 % error" in the paragraph after it, the table row giving the reason the stored total is refused in liquid, "5.8 % high" and "5.5 % fewer moles" in § "Known limitations", and the 24.055 L/mol molar volume in § "Agent amount".

**Why it matters.** The 5.8 % bias is the reason the stored total is refused in millilitres of liquid. If the reference temperature changed and these figures did not, a reader would be given the wrong size for that bias, and no check would say so.

**Checked 2026-11-22**, at `d4e8200c`. `grep -n "derived:" docs/MODEL.md | grep REFERENCE_TEMPERATURE` prints nothing, so no figure carries a marker naming the constant as an input. The paragraphs that write "20 °C" now carry `provenance:` markers from `#2142`, which tie the 20 and not the figures computed from it. Since `#2109` moved the interface sections, some of the figures are in `docs/INTERFACE.md`: "reads 5.8% high", the row "The conversion reads a store 5.8% high", the 17 mL step and "the 5.8 % error". In `docs/MODEL.md`, the paragraph in § "Known limitations" that opens "`core/liquid_agent.py` is where an amount leaves the unit" says "reads a store 5.8 % high" with no marker at all. `test_the_reference_condition_gap_is_the_ratio_of_molar_volumes` in `tests/reference/test_known_limitations_figures.py` computes the 5.8 % and the 5.5 % from the constants, so today the figures and the constant agree.

**Done when.** Each figure computed from the 20 °C reference temperature, in `docs/MODEL.md` and in `docs/INTERFACE.md`, carries a marker naming `core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20` as an input, so the documentation check refuses the figure when the reference temperature changes. Where a figure also depends on 37 °C, which no module stores, the marker says so or the item records why it cannot be tied.

**Generator check.** A re-entry of `PL-5L84`, closed 2026-11-11, which tied each written 20 °C to the stored constant and left the figures computed from it untied. The misread fact is the link between a document sentence and the tree fact it restates, which `PL-4FBP` states.
