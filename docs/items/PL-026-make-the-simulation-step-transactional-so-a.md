---
id: PL-026
title: Make the simulation step transactional so a halt leaves no partial state
priority: P1
effort: M
status: ready
classes: safety, ux
touches: src/anesthesia_sim/core/respiratory_system.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/agent_simulation_validation.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md
added: 2026-08-24
---

**Problem.** PL-018 made a failed step halt the run and warn that "the values
shown may not reflect a completed step", but the metrics and chart traces are
still drawn at whatever value the abandoned step left them:
`RespiratorySystem.advance()` applies five sub-exchanges in sequence and a
guard can reject the fifth after the first four have mutated state.

**Why it matters.** `CLAUDE.md` prefers an obvious failure state to a
plausible-looking number when correctness cannot be established. The numbers
left on screen are an artifact of the order the operators were applied in -
step 5 having run against step 2's output - not evidence of where the model
broke down.

**Decision (2026-08-24).** Roll the step back rather than treat the display.
A run's dynamic state is eight floats, so rollback is cheap and explicit, and
the display question dissolves: the metrics keep showing the last completed
step, which is a real solution of the model. The diagnosis moves into the
`SimulationNumericalError` message, where it can name the invariant and the
step size a reader can act on. Rejected options, the state inventory, and the
reasoning are in `docs/WORKING_NOTES.md` under "Decided, not yet implemented".

**Where.** `src/anesthesia_sim/core/respiratory_system.py` (`advance`,
`_advance_step`) and the five classes holding dynamic state:
`src/anesthesia_sim/core/circuit.py`, `src/anesthesia_sim/core/alveolar.py`,
`src/anesthesia_sim/core/tissue.py`, `src/anesthesia_sim/core/blood.py`,
`src/anesthesia_sim/core/agent_simulation_validation.py`. Also
`src/anesthesia_sim/app/simulation_view.py` and `docs/MODEL.md`.

**First step.** Give each compartment `capture_state()` / `restore_state()`
over its own dynamic fields, rather than reaching into them from
`RespiratorySystem`. A field added later without its capture then fails
locally and visibly instead of leaving a partial restore that looks complete.

**Done when.** A failed step leaves every dynamic value bit-identical to its
pre-step value, a regression test asserts that rather than approximate
agreement, the diagnosis has moved into the `SimulationNumericalError`
message, and `docs/MODEL.md` and `advance()`'s docstring stop promising
partial state.
