---
id: PL-RJN9
title: The agent cost View's two captions in src/anesthesia_sim/app/agent_cost.py write '20 degrees C' as text, a second copy of core/liquid_agent.py's REFERENCE_TEMPERATURE_CELSIUS, so a change to the reference temperature would leave the captions naming the old one
priority: P1
effort: S
status: done
classes: defect, safety
feature: one-source-of-truth
touches: src/anesthesia_sim/app/agent_cost.py, src/anesthesia_sim/app/display_units.py, tests/unit/test_agent_cost.py, tests/unit/test_display_units.py
added: 2026-11-07
closed: 2026-11-11
pr: 2136
payoff: the agent cost View's captions always name the temperature and pressure the conversion used, so a change to either cannot leave a correct figure under a wrong label
verify: ! grep -qF 'at 20 degrees C' src/anesthesia_sim/app/agent_cost.py
reenters: PL-40SJ
---

**Problem.** The agent cost View's two captions in src/anesthesia_sim/app/agent_cost.py write '20 degrees C' as text, a second copy of core/liquid_agent.py's REFERENCE_TEMPERATURE_CELSIUS, so a change to the reference temperature would leave the captions naming the old one

**Checked 2026-11-09:** `LIQUID_CAPTION_TEMPLATE` and `VAPOUR_CAPTION_TEMPLATE` in `src/anesthesia_sim/app/agent_cost.py` still say "at 20 degrees C" as text, while `REFERENCE_TEMPERATURE_CELSIUS: Final = 20.0` in `src/anesthesia_sim/core/liquid_agent.py` is the value the conversion uses. The vapour caption's "1 atm" is likewise a second copy of `STANDARD_ATMOSPHERE_PA` in that module, which the conversion also uses.

**Why it matters.** The captions state the conditions of a displayed clinical volume. If the reference temperature or pressure changed, the figure would follow and the caption would still name the old condition, so a learner would read a correct number under a wrong label. `tools/literal_home_check.py` does not read a number written inside a string, so nothing would catch it.

**Done when.** Both captions take the temperature and the pressure from the constants the conversion uses, and a test asserts that each caption names the values those constants hold. Work it with `PL-11Z9`, which changes the same captions.

**Placed in v0.7.0 on 2026-11-10 (project owner, ratified, over deferring it to the next gate).** `ROADMAP.md` § "v0.7.0 - the schematic" names this item in Required scope entry 13, with `PL-HQPF` (every agent amount on screen names 20 °C and 1 atm). Work the two together, because both change the agent cost View's captions.

**Generator check.** An instance of `PL-40SJ`'s fact (the value of a named constant, read from its one definition rather than typed again at the use), filed after that head closed on 2026-10-03. That head's fix, `tools/literal_home_check.py`, reads numeric literals and not numbers inside a string.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. `src/anesthesia_sim/app/agent_cost.py` did not exist at 817a4d88. The captions arrived in 26eb4e39 (`PL-B396`, #1932, 2026-11-02), which built v0.7.0's agent cost View. As a `safety` finding it re-enters the gate regardless of presence, and it is deferred on the not-live terms recorded in `deferred-from`.

**Built 2026-11-11, with `PL-HQPF`.** `display_units.py` builds `REFERENCE_TEMPERATURE_LABEL` ("20 °C") from `REFERENCE_TEMPERATURE_CELSIUS`, and `REFERENCE_CONDITION_LABEL` ("20 °C and 1 atm") from it and from a new `REFERENCE_PRESSURE_PA` in `core/liquid_agent.py`. That constant equals `STANDARD_ATMOSPHERE_PA`, and the molar volume now divides by it, so the label and the conversion read one pressure. Both captions in `agent_cost.py` read the labels. `test_the_reference_condition_label_names_the_conversions_temperature_and_pressure` checks the constants and the labels against 20 °C and one standard atmosphere, typed from `docs/MODEL.md` § "Agent amount". On the code before the fix, `test_each_caption_says_what_its_unit_measures` fails with the caption "Liquid used by the vaporizer, at 20 degrees C." against the expected "at 20 °C.".
