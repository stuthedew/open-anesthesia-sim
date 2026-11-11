---
id: PL-HQPF
title: The accounting panel's unit caption ('Litres of equivalent pure agent gas') and the schematic's unit ('mL vapour') do not name the condition an agent amount is stated at, 20 °C and 1 atm, so a learner cannot tell that an amount held in the body is stated at room temperature and reads 5.8% high
priority: P1
effort: M
status: done
classes: defect, safety
touches: src/anesthesia_sim/app/display_units.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/agent_cost.py, src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/core/liquid_agent.py, tests/unit/test_display_units.py, tests/unit/test_dashboard_frame.py, docs/MODEL.md
added: 2026-11-10
closed: 2026-11-11
pr: 2136
payoff: every agent amount on screen says it is stated at 20 °C and 1 atm, so a learner can tell an amount held in the body from one at body temperature
verify: grep -q 'def test_every_agent_amount_unit_names_the_reference_condition' tests/unit/test_display_units.py
---

**Problem.** The accounting panel's unit caption ('Litres of equivalent pure agent gas') and the schematic's unit ('mL vapour') do not name the condition an agent amount is stated at, 20 °C and 1 atm, so a learner cannot tell that an amount held in the body is stated at room temperature and reads 5.8% high

**Checked 2026-11-10:** `ACCOUNTING_UNIT_CAPTION` in `src/anesthesia_sim/app/dashboard_frame.py` is "Litres of equivalent pure agent gas". `DisplayUnit.AGENT_VAPOUR_MILLILITRES` in `src/anesthesia_sim/app/display_units.py` is "mL vapour". Neither names a temperature or a pressure. Only the agent cost View does, in `src/anesthesia_sim/app/agent_cost.py`, where "20 degrees C" is typed as text (`PL-RJN9`). The module docstring of `src/anesthesia_sim/core/liquid_agent.py` says the alveolar, venous and tissue stores are at body temperature, "carry the 20 °C condition only as a label", and are overstated by 5.8% (310.15 K / 293.15 K = 1.058).

**Why it matters.** An agent amount is a volume of vapour, and a volume of gas means nothing without its temperature and pressure. The accounting panel and the schematic show amounts held in the body with no condition beside them, so a learner has no way to know they are stated at 20 °C and read 5.8% high against body temperature. The safety-critical standard counts a correct number with an incomplete label as a failure.

**Decision (project owner, 2026-11-10, ratified, over converting the body's stores to 37 °C for display).** Label the amounts with the one condition the model states them at. The accounting panel adds the delivered, exhausted and stored amounts, and they sum only when all are stated at one condition. Converting the stores would show a truer stored figure and an account that no longer balances.

**Done when.** One label for the reference condition is built from `REFERENCE_TEMPERATURE_CELSIUS` and `STANDARD_ATMOSPHERE_PA` in `core/liquid_agent.py`. The accounting panel's caption, the schematic's unit and the cost View's two captions read it. A test asserts that each names the values those constants hold. `docs/MODEL.md` § "Known limitations" says where the condition is shown. The wording and placement are placeholders; that the condition is on screen is not. Work it with `PL-RJN9` (the cost captions type the temperature as text), `PL-11Z9` (which changes the same captions) and `PL-N3SK` (the specification says no liquid figure is on screen).

**Gate disposition, put to the owner on 2026-11-10.** The item is recorded as deferred from v0.7.0 so that the store is valid, on the grounds its `deferred-from` gives. **Recommended:** v0.7.0 takes it, with `PL-RJN9`, because the label is small and v0.7.0 is the release that shows an agent cost stated at this condition. Taking it means adding it to the frozen list or to the release's required scope in `ROADMAP.md`, which is the owner's to approve.

**Answered 2026-11-10 (project owner, ratified, over deferring it to the next gate).** v0.7.0 takes this item, together with `PL-RJN9` (the cost captions type the temperature as text). `PL-LMJ8` made the roadmap edit on 2026-11-10: `ROADMAP.md` § "v0.7.0 - the schematic" names both items in Required scope entry 13 and in the frozen list's first group, and neither item carries `deferred-from` now.

**Generator check.** A one-off as a display gap. Its second half is `PL-RJN9`, which already records the typed copy as an instance of `PL-40SJ`'s fact.

**Built 2026-11-11, with `PL-RJN9` and `PL-11Z9`.** One label, `REFERENCE_CONDITION_LABEL` in `display_units.py`, is built from the conversion's constants (`PL-RJN9` says how). The accounting panel's caption reads "Litres of equivalent pure agent gas, at 20 °C and 1 atm". The schematic names the condition once, in its heading: "Where the agent is: each compartment's tension, and its amount in millilitres of vapour at 20 °C and 1 atm". It is not added to each container's amount label, because six repeats of the condition would widen every column without telling the reader more (placeholder placement, recorded under the owner's 2026-10-18 rule on look and placement). The cost View's vapour caption names both, and its liquid caption names the temperature only, since a liquid's volume barely changes with pressure. `docs/MODEL.md` § "Known limitations" ("It does not touch a concentration, and the screen names the condition beside every amount") now says where the condition is shown, and replaces the stale sentence that nothing on screen showed a converted amount. § "The compartment schematic: what its heights, amounts and share bar assert" quotes the new caption, and § "The agent-accounting panel" says the panel names the condition. `test_every_agent_amount_unit_names_the_reference_condition` checks all four places against the typed text "20 °C and 1 atm". On the code before the fix, `test_the_accounting_unit_caption_names_litres_of_agent_gas_and_its_condition` fails against the old caption "Litres of equivalent pure agent gas".
