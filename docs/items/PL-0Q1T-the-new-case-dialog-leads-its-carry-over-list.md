---
id: PL-0Q1T
title: The new-case dialog leads its carry-over list with circuit volume, the one entry in it a user cannot set, and it is now the interface's only mention of the parameter
status: untriaged
added: 2026-09-06
---

**Problem.** The new-case dialog leads its carry-over list with circuit volume, the one entry in it a user cannot set, and it is now the interface's only mention of the parameter

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `NEW_CASE_CARRYOVER_TEMPLATE`
(`src/anesthesia_sim/app/simulation_view.py`) reads "Circuit volume, fresh gas
flow, alveolar ventilation and cardiac output carry over." Every claim in it
is true - `SimulationController.set_agent` does preserve all four - but the
first of the four is not a setting the reader has, and after `PL-GYH2` retired
`SimulationController.set_circuit_volume` it is not one anybody has. The other
three are sliders.

**Why it matters.** This dialog is now the only place the interface names the
circuit volume at all, and it names it inside a list of settings that carry
over - which is a list of things a reader understands themselves to have
chosen. A reader who goes looking for the control it implies will not find
one. `CLAUDE.md`'s safety-critical standard counts what a display implies as
part of its correctness, and `.claude/rules/expert-review.md` asks for
interfaces without hidden modes or surprising defaults; a named setting with
no control is the mirror of that.

**Not a wrong statement, so not a defect of fact.** The question is whether
the sentence should name a parameter the reader cannot set. Two candidates:
drop it and let the sentence describe the three sliders, which is what the
reader can act on; or keep it and mark it as fixed, which tells the reader
something true they may want to know when switching agents. The first is
probably right - the dialog's job is to say what a discard costs, and a
parameter that cannot change is not part of that cost - but it is a judgment
about what the dialog is for, so it wants deciding rather than assuming.

**Where.** `src/anesthesia_sim/app/simulation_view.py`
(`NEW_CASE_CARRYOVER_TEMPLATE`), and the tests asserting its text.

**Found by** `PL-GYH2` while sweeping for interface strings the setter's
removal might have made stale. This one it did not; it made it lopsided.
