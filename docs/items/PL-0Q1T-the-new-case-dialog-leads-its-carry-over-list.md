---
id: PL-0Q1T
title: The new-case dialog leads its carry-over list with circuit volume, the one entry in it a user cannot set, and it is now the interface's only mention of the parameter
priority: P2
effort: S
status: done
classes: ux
feature: presentation-safety
milestone: v0.4.19
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py
added: 2026-09-06
closed: 2026-09-13
pr: 530
verify: uv run pytest tests/unit/test_simulation_view.py -q -k carry_over_sentence_names_only
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

**Decision needed — ANSWERED 2026-09-13, see below.** Does `NEW_CASE_CARRYOVER_TEMPLATE` name the circuit volume
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

**Answered 2026-09-13 (project owner): drop it.** `NEW_CASE_CARRYOVER_TEMPLATE`
now reads "Fresh gas flow, alveolar ventilation and cardiac output carry over.
Delivered {agent} starts at that agent's own 1 MAC." — three settings, all of
them sliders the reader has.

**The reasoning, recorded here and beside the constant.** The dialog exists to
tell a reader what discarding the case costs *them*, and that cost is
denominated in things they chose. A parameter with no control is not part of
it. Keeping it and marking it fixed would have been true, but it would have
spent the dialog's most-read sentence on a fact that changes no decision the
dialog is asking for.

**The class stays `ux`.** The brief offered to reclassify if the implied
control read as a presentation failure under `CLAUDE.md`'s standard rather than
an interface wart. It does not: every claim in the old sentence was true and no
displayed value was wrong.

**What the interface no longer mentions, and why that is not a loss.** This was
the only mention of the circuit volume anywhere in the interface. Its value and
provenance are `docs/MODEL.md`'s to carry, and `PL-4YY1` (record provenance for
the circuit volume and default fresh gas flow, P1, open) is the item that owes
it — not this dialog.

**The test asserts the property, not the string.** `PL-GYH2`'s finding was that
the parameter has no setter, so
`test_the_carry_over_sentence_names_only_settings_the_reader_can_set` checks
that the sentence names the three sliders and not the circuit volume. Rewording
the sentence needs no test edit; reintroducing the parameter fails.
