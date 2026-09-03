---
id: PL-10MX
title: Advance a caller over a duration by taking supported steps
priority: P2
effort: S
status: ready
classes: feature
feature: numerical-domain
touches: src/anesthesia_sim/core/simulation.py, src/anesthesia_sim/core/uptake_system.py, docs/MODEL.md
added: 2026-08-30
verify: uv run pytest -k advance_over
---

**Problem.** After PL-VP7N a caller that wants 30 s of simulated time gets a
`SimulationConfigurationError` for `advance(30.0)` and must write the loop
itself. Every caller that wanted a duration rather than a step now carries
the same three lines — `for _ in range(round(duration_s / step_s))` — and
this item's own diff added four copies of them to the test suite.

**Why it matters.** The refusal is right, but a refusal with no supported
route to the same end state pushes a caller toward the wrong workaround:
editing the constant, or calling `_advance_step`. A `advance_over(duration_s)`
on `SimulationState` that sub-steps at `MAXIMUM_SIMULATION_STEP_S` serves the
request correctly instead of refusing it, and is the answer to "the supported
step and the shipped step are the same number, so there is no headroom for a
coarser headless run" — the headroom a headless run actually needs is a
coarser *call*, not a coarser step.

**Where.** `core/simulation.py`. Probably `SimulationState` rather than
`AgentUptakeSystem`, since a duration is a statement about elapsed time and
that is the class that owns it.

**Worth deciding first.** What a non-integer number of steps does — refuse a
duration that is not a whole multiple of the step, or take a shorter final
step? Refusing is the safer default and keeps simulated time exactly
representable; it also keeps this from becoming a way to smuggle in a
variable step. Relatedly, PL-VM40 (derive simulated time from a step count)
may make this trivial or may subsume it: sequence them together.

**Done when.** A caller can ask for a duration and get it as supported steps,
elapsed time still advances exactly, a duration that does not divide the step
is refused with a message that says so, and `docs/MODEL.md` § "Supported
simulation step" records the route.

**What v0.4.1 does to this (added 2026-09-03).** This item cannot be scoped until
`PL-X9KD` reports. Its stated problem is that `advance(30.0)` is refused with a
`SimulationConfigurationError`, which depends on `MAXIMUM_SIMULATION_STEP_S`
continuing to exist. `PL-X9KD` explicitly leaves that open: "Decide what the
bound now means, or remove it and say why." If the bound goes, `advance_over`
collapses to a single exact step and this item is close to moot; if it stays -
on capacity-guard, scaling-and-squaring or observability grounds rather than
splitting error - the item stands with a new rationale and the same shape.
Either way the answer is `PL-X9KD`'s to give.