---
id: PL-2TWX
title: The agent cost View's two unit names, the accounting amounts' 'L' and the accounting caption's unit phrase are spelled outside app/display_units.py, which docs/INTERFACE.md says defines every spelling of an amount's unit
priority: P3
effort: S
status: done
classes: defect
feature: one-source-of-truth
milestone: v0.6.19
touches: src/anesthesia_sim/app/display_units.py, src/anesthesia_sim/app/agent_cost.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/preferences.py, docs/INTERFACE.md, tests/unit/test_display_units.py
added: 2026-11-21
closed: 2026-11-21
pr: 2196
payoff: A change to how a unit of agent amount is written reaches every place the interface writes it, so two Views cannot name one amount in two ways
tests: tests/unit/test_display_units.py::test_no_agent_amount_unit_is_spelled_outside_the_units_module, tests/unit/test_display_units.py::test_the_search_for_a_typed_amount_unit_finds_one_in_each_kind_of_string, tests/unit/test_display_units.py::test_the_cost_views_unit_names_are_the_members_full_spellings, tests/unit/test_display_units.py::test_the_formatters_write_the_members_labels, tests/unit/test_display_units.py::test_a_refused_bottle_volume_names_its_unit_from_the_member
reenters: PL-G84G
---

**Problem.** The agent cost View's two unit names, the accounting amounts' 'L' and the accounting caption's unit phrase are spelled outside app/display_units.py, which docs/INTERFACE.md says defines every spelling of an amount's unit

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and share bar assert" says "Each spelling of an amount's unit is defined once, in `app/display_units.py` (`DisplayUnit`). ... Every View reads its spellings from that file and defines none of its own." Three spellings are defined elsewhere:

- `UNIT_CHOICES` in `app/agent_cost.py` types "millilitres of liquid" and "litres of vapour" as literals. `DisplayUnit.AGENT_LIQUID_MILLILITRES.recorded` and `DisplayUnit.AGENT_VAPOUR_LITRES.recorded` hold the same two strings, and `AgentAmountUnit` in `app/formatting.py` holds them a third time. `tests/unit/test_agent_cost.py` asserts the literal.
- `format_agent_volume` in `app/formatting.py` passes the literal `"L"`. No `DisplayUnit` member has the label "L".
- `ACCOUNTING_UNIT_CAPTION` in `app/dashboard_frame.py` types "Litres of equivalent pure agent gas".

`git grep -n '"millilitres of liquid"\|"litres of vapour"' -- src/anesthesia_sim` lists `agent_cost.py`, `display_units.py` and `formatting.py`.

**Why it matters.** A unit's spelling changed in `DisplayUnit` would leave the agent cost View's selector and the accounting View's amounts on the old one, which is the failure the section's rule exists to prevent.

**Done when.** Each of the three spellings is read from `DisplayUnit`, and the check or test that guards the rule fails on a unit spelling typed outside `app/display_units.py`.

**Built 2026-11-21.** The agent cost View's two unit names are read from `DisplayUnit` through `AGENT_AMOUNT_UNIT_DISPLAY`. The accounting panel's unit is a new member, `DisplayUnit.ACCOUNTED_AGENT_LITRES`, which holds the caption's phrase "litres of equivalent pure agent gas" and the "L" written beside each amount. `format_agent_volume`, `format_agent_residual` and `ACCOUNTING_UNIT_CAPTION` read it. The refusal of a bottle volume also reads its unit from the member. No text on screen changes.

`test_no_agent_amount_unit_is_spelled_outside_the_units_module` in `tests/unit/test_display_units.py` reads every string in `app/` that is not a docstring, and fails on one that contains a spelling of an agent amount's unit outside `app/display_units.py`. It failed on `UNIT_CHOICES` before this change. It cannot search for the bare "L", because one letter is in most strings.

One thing stays as it was. The values of `AgentAmountUnit` in `app/formatting.py` are the words that the preferences file stores for a unit. They must not follow a change of spelling on screen, or a saved file would stop being read. The test leaves that class out and fails if the class stops holding those words.

The accounting panel writes litres of vapour as "L" under its caption, and the agent cost View writes the same unit as "L vapour". They are two members now. Whether the two Views should write the unit the same way is a wording question for the visual pass.

**Generator check.** A re-entry of `PL-G84G`, which gathered the units into `DisplayUnit` and closed on 2026-10-25. Its module says that no check reads strings, so nothing refused the next typed spelling, and `PL-B396` typed two in the agent cost View's selector eight days later. The fact is where a unit's spelling is defined. The new test refuses the next typed spelling of an agent amount's unit. Found by `PL-5FMC`, the check of the interface documents that the project owner asked for.

**Documents checked.** `docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and share bar assert" (changed) and § "The agent-accounting panel" (still true), `docs/ARCHITECTURE.md`'s line for `display_units.py` (still true), `docs/MODEL.md` § "Known limitations" (still true) and `README.md` (no unit spelling).
