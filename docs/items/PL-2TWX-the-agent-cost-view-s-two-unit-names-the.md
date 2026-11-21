---
id: PL-2TWX
title: The agent cost View's two unit names, the accounting amounts' 'L' and the accounting caption's unit phrase are spelled outside app/display_units.py, which docs/INTERFACE.md says defines every spelling of an amount's unit
status: untriaged
feature: one-source-of-truth
added: 2026-11-21
---

**Problem.** The agent cost View's two unit names, the accounting amounts' 'L' and the accounting caption's unit phrase are spelled outside app/display_units.py, which docs/INTERFACE.md says defines every spelling of an amount's unit

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and share bar assert" says "Each spelling of an amount's unit is defined once, in `app/display_units.py` (`DisplayUnit`). ... Every View reads its spellings from that file and defines none of its own." Three spellings are defined elsewhere:

- `UNIT_CHOICES` in `app/agent_cost.py` types "millilitres of liquid" and "litres of vapour" as literals. `DisplayUnit.AGENT_LIQUID_MILLILITRES.recorded` and `DisplayUnit.AGENT_VAPOUR_LITRES.recorded` hold the same two strings, and `AgentAmountUnit` in `app/formatting.py` holds them a third time. `tests/unit/test_agent_cost.py` asserts the literal.
- `format_agent_volume` in `app/formatting.py` passes the literal `"L"`. No `DisplayUnit` member has the label "L".
- `ACCOUNTING_UNIT_CAPTION` in `app/dashboard_frame.py` types "Litres of equivalent pure agent gas".

`git grep -n '"millilitres of liquid"\|"litres of vapour"' -- src/anesthesia_sim` lists `agent_cost.py`, `display_units.py` and `formatting.py`.

**Why it matters.** A unit's spelling changed in `DisplayUnit` would leave the agent cost View's selector and the accounting View's amounts on the old one, which is the failure the section's rule exists to prevent.

**Done when.** Each of the three spellings is read from `DisplayUnit`, and the check or test that guards the rule fails on a unit spelling typed outside `app/display_units.py`.
