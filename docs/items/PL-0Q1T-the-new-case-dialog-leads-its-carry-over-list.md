---
id: PL-0Q1T
title: The new-case dialog leads its carry-over list with circuit volume, the one entry in it a user cannot set, and it is now the interface's only mention of the parameter
priority: P2
effort: S
status: needs-decision
classes: ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py
added: 2026-09-06
---

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

**Done when.** `NEW_CASE_CARRYOVER_TEMPLATE` either names only settings the
reader can act on, or names the circuit volume as fixed rather than as
something that carries over; the choice is recorded here with its reasoning;
and the tests asserting the dialog's text assert whichever sentence ships.

**Found by** `PL-GYH2` while sweeping for interface strings the setter's
removal might have made stale. This one it did not; it made it lopsided.

**Decision needed.** Does `NEW_CASE_CARRYOVER_TEMPLATE` name the circuit volume
at all? Drop it, so the sentence describes only the three settings the reader
can act on; or keep it and mark it as fixed rather than as something that
carries over. The brief argues the first - the dialog's job is to say what
discarding a case costs, and a parameter nobody can change is not part of that
cost.

**Classed `ux` rather than `safety`, and it can be overruled.** Every claim in
the sentence is true and no displayed value is wrong; what is lopsided is that
the list implies a control the reader does not have. If that reads as a
presentation failure under `CLAUDE.md`'s standard rather than an interface
wart, the class changes and the band goes with it.
