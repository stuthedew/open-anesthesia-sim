---
id: PL-0MLQ
title: Refuse a setting outside the documented supported input range
priority: P1
effort: M
status: done
classes: safety
feature: numerical-domain
touches: src/anesthesia_sim/core/respiratory_system.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/patient.py, docs/MODEL.md
added: 2026-08-30
closed: 2026-09-02
pr: 191
verify: uv run pytest tests/unit/test_respiratory_system_failure.py && grep -q 'def test_a_setting_outside_the_supported_range_is_refused_by_the_system' tests/unit/test_respiratory_system_failure.py
---

**Problem.** `docs/MODEL.md` § "Supported input ranges" declares a closed
supported interval for each of the four controls — fresh gas flow 0 to
10 L/min, alveolar ventilation 0 to 12, cardiac output 0 to 10, delivered
concentration 0 to the agent's vaporizer maximum. Only the last is enforced.
`RespiratorySystem.set_cardiac_output(1000.0)` is accepted, as are a fresh
gas flow of 500 L/min and an alveolar ventilation of 200 L/min: the
compartment setters check `require_nonnegative_finite` and nothing else. The
interface's sliders are the only thing keeping a run inside the domain the
verification gates cover.

**Why it matters.** This is PL-VP7N's defect one axis over, and the same
argument applies to it: the splitting-error bound
($`C_{\max} = 2.29\times10^{-3}\ \mathrm{s^{-1}}`$) and everything derived
from it — the displayed resolution, the supported step — are measured over
the trajectories *these ranges* produce. A caller outside them gets a number
with no measured bound, and `docs/MODEL.md` says the ranges "define the
verification domain". Found while implementing PL-VP7N, where reaching the
capacity guard at a supported step needed a compartment the interface cannot
build.

**Where.** `core/circuit.py` (`set_fresh_gas_flow`), `core/alveolar.py`
(`set_alveolar_ventilation`), `core/patient.py` (`set_cardiac_output`), and
the `RespiratorySystem` setters that forward to them.

**Worth deciding first.** Whether the limits belong in `core/` at all, or
whether the honest statement is that `core/` supports any nonnegative flow
and it is the *verification* that is bounded. The sliders' maxima are
interface choices (`app/simulation_view.py`), and `core/` importing them
would invert the layering — so if they move into `core/`, they move as the
model's own declared domain with `app/` checked against it, the shape
PL-VP7N used for the step. Note also that the alveolar gas volume, which has
no slider at all, is unbounded above and below in the same way.

**Done when.** Either the four ranges are declared and enforced in `core/`
with `app/` checked against them and `docs/MODEL.md` updated, or
`docs/MODEL.md` is corrected to say what is actually true about who enforces
what.

**Resolved: declared and enforced in `core/`** (2026-09-02), taking the first
branch. The open question was whether these are the model's ranges or only the
verification's, and it was settled by measuring rather than argued. On the
*unperfused load, then dial off* trajectory the documented
$`2.29\times10^{-3}\ \mathrm{s^{-1}}`$ bound is measured on, the splitting
coefficient scales roughly in proportion to the flows: this item's own
`set_cardiac_output(1000.0)` reaches $`9.12\times10^{-2}\ \mathrm{s^{-1}}`$,
40 times the bound and 91 counts of the displayed resolution, so the alveolar
readout is wrong in its first decimal while presenting itself as a settled
two-decimal value. Doubling all three flows doubles the coefficient; a fresh
gas flow of 500 L/min reaches 2.5 times it and an alveolar ventilation of
200 L/min 1.5 times. Outside the ranges the number is therefore wrong rather
than merely unverified, which takes the choice out of the mechanism-preference
category the item framed it in.

`core/supported_ranges.py` declares the three intervals and the guards;
`BreathingCircuit`, `AlveolarCompartment` and `PatientCompartments` refuse a
value outside their own, in the setter and in `__post_init__`, so every path —
`RespiratorySystem`'s forwarding setters, the controller, a direct compartment
construction — passes one guard. `app/simulation_view.py` imports the
constants for its sliders instead of declaring them, and
`test_the_sliders_span_the_supported_input_ranges` reads the endpoints off the
constructed controls and drives each through the real controller, so a slider
that reached past the domain or stopped short of it fails.

The guard sits on the compartment rather than on the coupled system, the
opposite of `MAXIMUM_SIMULATION_STEP_S`, because a flow is persistent state
reachable three ways where a step is one call's argument — and because a
compartment advanced alone is exact at any step but is not exempt from a
setting the model does not support.

**The volumes are not covered** and are now `PL-GYH2`: the item's note about
the alveolar gas volume was right, `SimulationController.set_circuit_volume`
has the same gap, and both need a decision about whether either is a control
at all before a range can be declared for them. `docs/MODEL.md` § "Supported
input ranges" states the gap rather than leaving it silent.
