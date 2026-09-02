---
id: PL-WVSK
title: Nothing distinguishes a concentration fraction from a percent at the type level, and two boundaries convert implicitly
status: needs-decision
priority: P2
effort: M
classes: refactor
touches: src/anesthesia_sim/core, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py
added: 2026-09-02
---

**Problem.** Every quantity in `core/` is a bare `float` carrying its unit in
the identifier only. Two boundaries convert between fraction and percent
inline: `AgentUptakeSystem.for_agent()` divides `mac_percent` and
`max_delivered_concentration_percent` by 100, and
`_handle_delivered_concentration_change` divides the slider's value by 100.
`SimulationSnapshot` carries `max_delivered_concentration_percent` and
`delivered_concentration_fraction` as adjacent fields, and the delivered
slider reads its `max` from one and its `value` from the other.

**Why it matters.** The runtime guards catch the gross error - a percent
above 1 handed to `require_concentration_fraction` is refused - but not the
middle, where `0.5` is a valid fraction (50%) and a valid percent (0.5%) and
passes every guard in the codebase. `CLAUDE.md`'s safety-critical standard
asks for "unit-aware types or equivalent safeguards where practical" and for
avoiding implicit unit conversions; this is the one place the standard's own
words are not met.

No defect is known to follow from it today. This is a preventive change, and
that is why it is a decision rather than a fix.

**Where.** `src/anesthesia_sim/core/uptake_system.py` `for_agent()`;
`src/anesthesia_sim/app/simulation_view.py`
`_handle_delivered_concentration_change()`;
`src/anesthesia_sim/app/controller.py` `SimulationSnapshot`.

**Decision needed.** Whether to introduce the distinction, and how far:

1. Boundary only - `typing.NewType` for `Fraction` and `Percent` on the four
   control setters, `AgentParameters` and `SimulationSnapshot`, plus two
   named conversions in one module. Zero runtime cost, enforced by the
   existing strict `mypy` gate, and it converts a review question into a
   check.
2. Whole core, every quantity including volumes, flows and times.
3. Neither - the identifier suffix convention plus the range guards are
   judged sufficient, recorded with the reason.

Option 1 is what the audit recommended, and its timing argument is the part
worth weighing: `PL-DHV7` (express compartment concentrations in MAC
multiples as a display unit) adds a third concentration convention, so this
is cheapest before that lands and most expensive after.

**Done when.** The decision is recorded, and if types are introduced, `mypy`
rejects a percent passed where a fraction is expected in a test asserting it.
