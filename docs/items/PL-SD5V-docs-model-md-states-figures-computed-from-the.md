---
id: PL-SD5V
title: docs/MODEL.md states figures computed from the 20 °C reference temperature (the 5.8 % store bias, 5.5 % fewer moles, 24.055 L/mol, the 17 mL step) with no derived: marker naming REFERENCE_TEMPERATURE_CELSIUS, so changing the reference temperature leaves them stale with no refusal
status: untriaged
feature: model-claims-held-by-tests
added: 2026-11-11
---

**Problem.** docs/MODEL.md states figures computed from the 20 °C reference temperature (the 5.8 % store bias, 5.5 % fewer moles, 24.055 L/mol, the 17 mL step) with no derived: marker naming REFERENCE_TEMPERATURE_CELSIUS, so changing the reference temperature leaves them stale with no refusal

**Found by.** Blind review pass 1 on `PL-5L84` (#2142). The reviewer changed `REFERENCE_TEMPERATURE_CELSIUS` to 25 in a copy of the tree, and the documentation check then reported only the paragraphs that write "20 °C". The figures computed from it stayed silent: "reads 5.8% high" and the 17 mL step in § "Displayed precision" (the paragraph saying the stored total is refused in millilitres of liquid), "the 5.8 % error" in the paragraph after it, the table row giving the reason the stored total is refused in liquid, "5.8 % high" and "5.5 % fewer moles" in § "Known limitations", and the 24.055 L/mol molar volume in § "Agent amount".

**Why it matters.** The 5.8 % bias is the reason the stored total is refused in millilitres of liquid. If the reference temperature changed and these figures did not, a reader would be given the wrong size for that bias, and no check would say so.

**Done when.** Each of those figures carries a `derived:` marker naming `core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20` as an input, so `tools/doc_check.py check` refuses it when the reference temperature changes. Where a figure also depends on 37 °C, which no module stores, the marker says so or the item records why it cannot be tied.
