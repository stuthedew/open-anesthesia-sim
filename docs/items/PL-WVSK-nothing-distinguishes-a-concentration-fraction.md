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

**Why it matters.** The runtime guards catch the gross error but not the
middle, where one number is a plausible reading under either convention and
passes every guard in the codebase. `CLAUDE.md`'s safety-critical standard
asks for "unit-aware types or equivalent safeguards where practical" and for
avoiding implicit unit conversions; this is the one place the standard's own
words are not met.

**Measured 2026-09-02, and the audit's example was wrong.** The capture said
`0.5` was "a valid fraction (50%) and a valid percent (0.5%)" passing every
guard. Run against a sevoflurane system, `set_delivered_concentration(0.5)`
is **refused** - the vaporizer maximum is 8%, so the fraction `0.08` caps it
and a percent mistaken for a fraction is caught above that. The confusable
band is therefore bounded above by the agent's own dial maximum, not open.

It is not empty, which is the part that survives. Both
`set_delivered_concentration(0.05)` and `set_delivered_concentration(0.0005)`
are accepted, and they are 5% and 0.05% - two orders of magnitude apart,
clinically a full dial setting against a rounding error, and nothing in the
type system, the guards or the identifier names distinguishes the intent. So
the finding holds at a narrower width than it was first written up as: the
gap is `0` to the vaporizer maximum rather than `0` to `1`.

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
