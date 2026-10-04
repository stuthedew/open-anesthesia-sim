---
id: PL-8W1W
title: SimulationState.step_count and simulation_step_s can be assigned after construction without any check - state.step_count = 5 stores a bare int, and = -3 after a step makes elapsed_s raise - the shape PL-LBQY records for the compartments' flows, on the run's own state; nothing in src writes either outside advance and reset; decide it with PL-LBQY: a __setattr__ guard, read-only fields, or the window recorded as accepted (found reviewing #1354)
priority: P1
effort: S
status: ready
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/simulation.py, tests/unit/test_simulation.py
added: 2026-10-04
payoff: the run clock can no longer be moved by a write nothing checked, so the time shown beside every value, and every mark and control change stamped with it, comes from a count and a step the simulator checked
verify: grep -q 'def test_a_count_or_a_step_written_onto_a_built_state_is_refused_at_the_write' tests/unit/test_simulation.py
---

**Problem.** SimulationState.step_count and simulation_step_s can be assigned after construction without any check - state.step_count = 5 stores a bare int, and = -3 after a step makes elapsed_s raise - the shape PL-LBQY records for the compartments' flows, on the run's own state; nothing in src writes either outside advance and reset; decide it with PL-LBQY: a __setattr__ guard, read-only fields, or the window recorded as accepted (found reviewing #1354)

**Reproduced 2026-10-04, at triage.** On Python 3.14.7, against `main` at
`8cc0698d`,
`uv run python -c "from anesthesia_sim.core.simulation import SimulationState; from anesthesia_sim.core.simulation_step import SimulationStep; s = SimulationState(); s.step_count = 5; print(type(s.step_count).__name__, s.step_count, s.elapsed_s); s.advance(SimulationStep(0.1)); s.simulation_step_s = 0.5; print(type(s.simulation_step_s).__name__, s.step_count, s.elapsed_s); s.step_count = -3; s.elapsed_s"`
printed `int 5 0.0`, then `float 6 3.0`, then raised
`SimulationConfigurationError` ("a case instant of -1.5 s is outside the
supported run length"). A fresh state took a bare count of 5 with no step to
multiply it by, the pair `__post_init__` refuses, and read 0 s. One step on,
it took a bare `float` step of 0.5 s, five times the largest supported step,
and its clock read 3.0 s for a system advanced 0.1 s. A negative count was
then taken without complaint and refused only when `elapsed_s` was next read,
as a run-length error naming an instant nobody handed in. Nothing in `src/`
writes either field outside `advance` and `reset`, and no test writes either
after construction.

**Decided by `PL-LBQY`'s answer.** The capture asked for this to be decided
with `PL-LBQY`, which the project owner answered on 2026-10-04 (ratified) for
the same `__setattr__` guard over frozen compartments and over accepting the
window. This triage applies that answer to the run's own state, so one pattern
holds a checked field on every mutable core record; it is this pass's
application of a ratified answer, not a separate decision, and reopens on
ordinary evidence.

**Why it matters.** `elapsed_s` is the run's clock: the controller copies it
into every snapshot, moves the run's definition to it, crosses marks at it and
stamps each recorded control change with it, so a count or a step written past
the checks moves the time a learner reads beside every value. No interface
path reaches it, since the controller holds its state privately and
`mypy --strict` refuses either assignment in `src/`; what reaches it is a
caller `mypy` does not read, such as a test, a notebook or a value typed
`Any`, as for `PL-LBQY`'s flows. For that caller a step five times the
supported maximum is taken silently and the clock reads five times the
simulated time, and a negative count surfaces later as a run-length refusal
that blames the span rather than the write.

**Done when.** Assigning `step_count` or `simulation_step_s` on a built
`SimulationState` runs the checks `__post_init__` runs, at the write and
before the field changes, so a bare `int` count, a negative one and a step not
built as a `SimulationStep` are each refused at the assignment with the
exception `__post_init__` raises for it, and the field keeps what it held; a
count past zero left with no step, or a pair past the supported run length, is
refused there too. `advance` and `reset` still write both, and the
reproduction above stops at its first assignment. A test in
`tests/unit/test_simulation.py` named
`test_a_count_or_a_step_written_onto_a_built_state_is_refused_at_the_write`
pins it.
