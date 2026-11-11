---
id: PL-HQPF
title: The accounting panel's unit caption ('Litres of equivalent pure agent gas') and the schematic's unit ('mL vapour') do not name the condition an agent amount is stated at, 20 °C and 1 atm, so a learner cannot tell that an amount held in the body is stated at room temperature and reads 5.8% high
priority: P1
effort: M
status: ready
classes: defect, safety
touches: src/anesthesia_sim/app/display_units.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/agent_cost.py, src/anesthesia_sim/app/qt_schematic.py, tests/unit/test_display_units.py, docs/MODEL.md
deferred-from: v0.7.0 - present at the freeze (817a4d88 holds the accounting caption) and not on the frozen list; found by the 2026-11-10 audit. The hazard is an incomplete label, not a wrong value: checked 2026-11-10, each amount on screen is correct in the unit docs/MODEL.md § 'Agent amount' defines, and a learner who assumes body temperature misreads a stored amount by 5.8%. Whether v0.7.0 takes it instead was put to the owner on 2026-11-10
added: 2026-11-10
payoff: every agent amount on screen says it is stated at 20 °C and 1 atm, so a learner can tell an amount held in the body from one at body temperature
verify: grep -q 'def test_every_agent_amount_unit_names_the_reference_condition' tests/unit/test_display_units.py
---

**Problem.** The accounting panel's unit caption ('Litres of equivalent pure agent gas') and the schematic's unit ('mL vapour') do not name the condition an agent amount is stated at, 20 °C and 1 atm, so a learner cannot tell that an amount held in the body is stated at room temperature and reads 5.8% high

**Checked 2026-11-10:** `ACCOUNTING_UNIT_CAPTION` in `src/anesthesia_sim/app/dashboard_frame.py` is "Litres of equivalent pure agent gas". `DisplayUnit.AGENT_VAPOUR_MILLILITRES` in `src/anesthesia_sim/app/display_units.py` is "mL vapour". Neither names a temperature or a pressure. Only the agent cost View does, in `src/anesthesia_sim/app/agent_cost.py`, where "20 degrees C" is typed as text (`PL-RJN9`). The module docstring of `src/anesthesia_sim/core/liquid_agent.py` says the alveolar, venous and tissue stores are at body temperature, "carry the 20 °C condition only as a label", and are overstated by 5.8% (310.15 K / 293.15 K = 1.058).

**Why it matters.** An agent amount is a volume of vapour, and a volume of gas means nothing without its temperature and pressure. The accounting panel and the schematic show amounts held in the body with no condition beside them, so a learner has no way to know they are stated at 20 °C and read 5.8% high against body temperature. The safety-critical standard counts a correct number with an incomplete label as a failure.

**Decision (project owner, 2026-11-10, ratified, over converting the body's stores to 37 °C for display).** Label the amounts with the one condition the model states them at. The accounting panel adds the delivered, exhausted and stored amounts, and they sum only when all are stated at one condition. Converting the stores would show a truer stored figure and an account that no longer balances.

**Done when.** One label for the reference condition is built from `REFERENCE_TEMPERATURE_CELSIUS` and `STANDARD_ATMOSPHERE_PA` in `core/liquid_agent.py`. The accounting panel's caption, the schematic's unit and the cost View's two captions read it. A test asserts that each names the values those constants hold. `docs/MODEL.md` § "Known limitations" says where the condition is shown. The wording and placement are placeholders; that the condition is on screen is not. Work it with `PL-RJN9` (the cost captions type the temperature as text), `PL-11Z9` (which changes the same captions) and `PL-N3SK` (the specification says no liquid figure is on screen).

**Gate disposition, put to the owner on 2026-11-10.** The item is recorded as deferred from v0.7.0 so that the store is valid, on the grounds its `deferred-from` gives. **Recommended:** v0.7.0 takes it, with `PL-RJN9`, because the label is small and v0.7.0 is the release that shows an agent cost stated at this condition. Taking it means adding it to the frozen list or to the release's required scope in `ROADMAP.md`, which is the owner's to approve.

**Answered 2026-11-10 (project owner, ratified, over deferring it to the next gate).** v0.7.0 takes this item, together with `PL-RJN9` (the cost captions type the temperature as text). Still to do, in the commit that edits `ROADMAP.md`: add both ids to v0.7.0's section there, remove the `deferred-from` line from both items, and correct the roadmap's statements that every id in v0.7.0's Required scope is closed (the current-baseline paragraph and row 9 of the timeline). The session that recorded this answer stopped before that edit because it had passed its token budget, and it continues after a reset.

**Generator check.** A one-off as a display gap. Its second half is `PL-RJN9`, which already records the typed copy as an instance of `PL-40SJ`'s fact.
