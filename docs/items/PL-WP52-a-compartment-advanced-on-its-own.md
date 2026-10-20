---
id: PL-WP52
title: A compartment advanced on its own (BreathingCircuit.advance_fresh_gas, TissueGroup.advance, the blood compartment's advance) accepts any positive finite step, so it takes steps below MINIMUM_SIMULATION_STEP_S, where rounding is a growing share of what a step changes (measured on the coupled system, PL-YZ17); only AgentUptakeSystem.advance refuses them, and whether a compartment should too is undecided
priority: P3
effort: S
status: done
classes: defect
feature: numerical-domain
milestone: v0.6.0
touches: src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/simulation_step.py, tests/unit/test_tissue.py, tests/unit/test_blood.py, tests/unit/test_circuit.py, docs/MODEL.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
closed: 2026-10-19
pr: 1676
payoff: a compartment stepped on its own either refuses a step below the floor by name or is shown by measurement not to need one, so a caller stepping it finely cannot be handed a plausible number nothing checked
verify: grep -q 'def test_a_step_below_the_floor_is_refused_when_a_tissue_is_stepped_alone' tests/unit/test_tissue.py && grep -q 'def test_a_step_below_the_floor_is_refused_when_the_pool_is_stepped_alone' tests/unit/test_blood.py && grep -q 'def test_a_step_below_the_floor_is_refused_when_the_circuit_is_stepped_alone' tests/unit/test_circuit.py
not-delegable: the item ends in one of two states chosen on a measurement - a floor each compartment refuses below, with a test per compartment, or the measured error against step recorded with why none is needed - and a command written before the measurement could pin only the state chosen in advance; its touches reach src/anesthesia_sim/core besides, which delegation may never modify
---

**Problem.** A compartment advanced on its own (BreathingCircuit.advance_fresh_gas, TissueGroup.advance, the blood compartment's advance) accepts any positive finite step, so it takes steps below MINIMUM_SIMULATION_STEP_S, where rounding is a growing share of what a step changes (measured on the coupled system, PL-YZ17); only AgentUptakeSystem.advance refuses them, and whether a compartment should too is undecided

**Found 2026-10-03** while declaring the floor in `PL-YZ17`. The floor
binds the run: `require_supported_simulation_step` is called by
`AgentUptakeSystem.advance()` and `SimulationState`, and a compartment is only
ever stepped at a run's step by the former, after the guard. A compartment
stepped on its own - `BreathingCircuit.advance_fresh_gas`,
`TissueGroup.advance`, the blood compartment's `advance` - checks only
`require_positive_finite`, so it takes 1e-14 s without complaint. The rounding
mechanism `PL-YZ17` measured on the coupled system (a third of the change
wrong at 1e-14 s) is not specific to coupling, so a compartment stepped that
finely presumably shares it; that is inferred, not measured.

The case for leaving it: a compartment stepped alone is a building block whose
caller owns the step, the way `docs/MODEL.md` § "Supported input ranges" argues
the ceiling does not bind one, and no test steps one alone below the 0.1 s
`tests/reference/test_circuit_wash_in.py` uses. The case for the guard: the compartments are public, and a notebook
stepping one finely gets a plausible number. Measure a compartment alone first;
the decision follows from whether it shares the coupled system's growth.

**Reproduced 2026-10-03 at triage** on `81debc03`: `TissueGroup.advance`,
`VenousBloodCompartment.advance`, `BreathingCircuit.advance_fresh_gas` and
`BreathingCircuit.advance` each took a 1e-14 s step without error, while
`require_supported_simulation_step` refused it. At that one step the inferred
rounding showed: a tissue group built as `tests/unit/test_tissue.py` builds one
(time constant 480 s), stepped toward an arterial fraction of 1.0, returned 0 L
where the exact change, computed with `expm1`, is 8.3e-17 L, because
`exp(-step/tau)` rounds to exactly 1.0. The venous blood compartment of
`tests/unit/test_blood.py` (12 s) returned 5.77e-16 L against an exact
5.42e-16 L, 6.6% high. One step, not the growth curve this item asks for.

**Why it matters.** The compartments are public, and a caller stepping one
below the floor gets a plausible number with none of the run's refusal: at
1e-14 s, none at all for the tissue. That is the safety standard's plausible
value where an error state belongs, though no screen path reaches it today.

[superseded 2026-10-04: the owner's answer, below]
**Blocked on `PL-0GJC`** (the run's step as a validated type). That item's
session put to the owner on 2026-10-03 whether a compartment stepped on its own
takes the type. Its recommendation moves the compartment clause here, to be
decided on this item's measurement; the alternative, a floor-only type the
compartments take now, would answer this item with that work. Either way this
item's shape follows that answer, so it waits on it.

**Moved here from `PL-0GJC`, 2026-10-04** (project owner, 2026-10-04,
ratified, over a second, floor-only type the compartments take now): whether a
compartment stepped on its own takes a floor is decided on this item's
measurement, not by the run's type. `PL-0GJC` made the run's step a
`SimulationStep` (`src/anesthesia_sim/core/simulation_step.py`), which checks
both bounds when it is built. The compartments still take a plain float,
because the 0.1 s ceiling binds the run and a compartment stepped alone at
1 s is correct today, so the run's type cannot be theirs as it stands. If the
measurement says a compartment needs the floor, the same decision chooses how
it is carried: a floor check in each compartment's `advance`, or a floor-only
type beside `SimulationStep`, which is the larger change.

**Done when.** Each compartment stepped on its own below
`MINIMUM_SIMULATION_STEP_S` raises the simulator's own error, with a test per
compartment pinning it, or this brief records the measured error against step
for a compartment alone and why it needs no floor; `docs/MODEL.md` §
"Supported simulation step" says which.

**Checked 2026-10-19:** still real on `08f0f825`. Each compartment took a
1e-14 s step without error. `exponential_approach` now uses `expm1`, so one
step of a tissue no longer rounds to nothing, but the error still grows as the
step shrinks once steps accumulate.

**Measured 2026-10-19** with 10 000 steps of each compartment alone, each held
at a fraction of 0.01 and stepped toward 0.02. The tissue group was built as
`tests/unit/test_tissue.py` builds one, at 1 L/min (time constant 480 s). The
venous pool was built as `tests/unit/test_blood.py` builds one, at 5 L/min
(7.8 s). The circuit was 6 L at 6 L/min (60 s). The error is in what each
compartment changed by, as a share of the exact change computed with `expm1`
over the whole interval:

| Step | Tissue | Venous pool | Circuit |
| --- | --- | --- | --- |
| 0.1 s | 3.4e-15 | 1.6e-14 | 1.4e-15 |
| 1 ms | 2.7e-13 | 3.2e-15 | 1.5e-14 |
| 1 µs | 2.5e-11 | 8.4e-12 | 8.9e-13 |
| 1e-10 s | 3.3e-5 | 1.4e-6 | 3.3e-5 |
| 1e-14 s | 1.0 (no change at all) | 3.9e-2 | 4.1e-2 |

A compartment alone shares the coupled system's growth, so the decision this
brief deferred follows from the measurement. Each compartment's own `advance`
now refuses a step below the floor. It does so through one new guard,
`require_at_least_the_smallest_step` in `core/simulation_step.py`, which
`require_supported_simulation_step` also calls, so the floor and its message
have one home. A floor check was chosen over a floor-only type. A type would
need `SimulationStep` to become its subclass so the run could pass one to a
compartment, and the floor check refuses the same steps with nothing else
changed. `docs/MODEL.md` § "Supported simulation step" records the table and
the decision.

**Run against the code before the fix:** with `src/` stashed, `pytest
tests/unit/test_tissue.py tests/unit/test_blood.py tests/unit/test_circuit.py
-k below_the_floor` gave 12 failed, each `Failed: DID NOT RAISE
SimulationConfigurationError`.
