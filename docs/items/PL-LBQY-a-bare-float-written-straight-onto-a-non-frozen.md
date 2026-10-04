---
id: PL-LBQY
title: A bare float written straight onto a non-frozen compartment field (circuit.fresh_gas_flow_l_min = 1000.0) is caught only at the next equation_settings(), so for one tick the snapshot and the readouts carry an unchecked value and SimulationSnapshot's typed fields carry no runtime check of their own; decide whether a __setattr__ guard or frozen compartments moves the check to the write, or record the one-tick window as accepted (found reviewing #1350)
priority: P1
effort: M
status: needs-decision
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/patient.py, src/anesthesia_sim/core/supported_ranges.py, tests/unit/test_supported_ranges.py, tests/unit/test_state_capture.py, docs/MODEL.md
added: 2026-10-04
payoff: a flow nobody checked can never appear on the setting readout, and a Reset after a bad write cannot leave a paused run showing a hundred times the supported maximum with no notice
---

**Problem.** A bare float written straight onto a non-frozen compartment field (circuit.fresh_gas_flow_l_min = 1000.0) is caught only at the next equation_settings(), so for one tick the snapshot and the readouts carry an unchecked value and SimulationSnapshot's typed fields carry no runtime check of their own; decide whether a __setattr__ guard or frozen compartments moves the check to the write, or record the one-tick window as accepted (found reviewing #1350)

**Reproduced 2026-10-04** on `main` at `8f24fe78`:
`uv run python -c "from anesthesia_sim.app.controller import SimulationController; from anesthesia_sim.app.dashboard_frame import setting_readouts; from anesthesia_sim.core.simulation_step import SimulationStep; c = SimulationController(); c._state.uptake_system.circuit.fresh_gas_flow_l_min = 1000.0; print(setting_readouts(c.snapshot())[0].value_text); c.start(); exec('try: c.advance(SimulationStep(0.1))\nexcept TypeError as e: print(e); c.fail(str(e))'); exec('try: c.reset()\nexcept TypeError as e: print(e)'); s = c.snapshot(); print(setting_readouts(s)[0].value_text, s.is_running, s.failure_reason)"`
printed `1000.0 L/min`, then the `TypeError` naming `fresh_gas_flow_l_min` as
"not built as FreshGasFlow", once from the step and once from `reset()`, then
`1000.0 L/min False None`. So the snapshot copied a bare `float` into its
`FreshGasFlow` field and the readout beside the slider printed it; the next
step refused it where `equation_settings()` rebuilds the settings, and
`c.fail()`, standing in for the view's halt, failed the run. Reset, which
keeps settings, rebuilt the run definition from the same
`equation_settings()` and raised after it had already cleared the failure, so
the run stood paused, with no notice, at a fresh gas flow a hundred times the
supported maximum: the window outlasts the tick. `#1354` does not change it.
Its branch leaves `circuit.py`, `alveolar.py`, `patient.py`,
`uptake_system.py`, `governing_equations.py` and the snapshot's flow fields as
they are on `main`, and `SimulationSnapshot` gains no `__post_init__` there.

**Why it matters.** The setting readout is what a learner takes as in force,
and until the next step, and again after a Reset with no notice beside it, it
shows a flow the model was never run at and is not claimed over. No route
reaches it from the interface: all 24 writes to a compartment field in `src/`
are made by the compartment's own methods, every slider builds its flow's type
before the controller's setter, and `mypy --strict` refuses
`circuit.fresh_gas_flow_l_min = 1000.0` in `src/` as an incompatible
assignment. What reaches it is a caller `mypy` does not read, such as a test,
a notebook or a value typed `Any`, which is the caller
`require_fresh_gas_flow` exists for. `docs/MODEL.md` § "Supported input
ranges" lists four ways a flow gets in and says a bare `float` handed to any
of them is refused with a `TypeError`; an assignment to the field is a fifth
that none of them sees, and the snapshot that copies it has no check of its
own.

**Decision needed.** Should a flow written straight onto its compartment field
be refused at the write, and how? Today, in `src/`, the fields are written
only by the compartments' own methods: six trajectory writes a step through
`_write_state_vector`, which at 300x is 3 000 steps a wall second; a setting
write on each control change; restores on a rollback. Outside `src/`, tests
write fields directly and on purpose, to measure capture and reset, to move a
setting around its setter, or to swap a tissue group or a failing stand-in
onto the patient. Three options, the first two simulated on `main` with a
scratch pytest plugin over the whole suite:

**A `__setattr__` guard** on `BreathingCircuit`, `AlveolarCompartment` and
`PatientCompartments` that runs the flow's `require_*` when the flow field is
assigned, after which the setters' and `__post_init__`'s own calls are
redundant. A step costs 20.3 us without it and 19.9 us with it (median of
seven runs of 20 000 steps, inside noise), since only two of a step's six
trajectory writes land on those classes. Four test cases fail, the capture
and restore and the reset cases for the circuit and the alveoli in
`tests/unit/test_state_capture.py`, whose perturbation writes a bare `float`
onto the flow; the 680 integration and reference tests pass. It refuses the
type only. A dial written straight past the vaporizer maximum still runs: on
`main`, `system.circuit.delivered_concentration_percent = 50.0` ran 600 steps
to 20.13% inspired sevoflurane against an 8% maximum. So would a typed flow
outside a machine's declared range, which no shipped profile declares,
because both of those checks live only in the setters.

**Frozen compartments**, refusing any write not made by the compartment's own
methods, so every setter-held check and invariant holds at the write, the dial
and the machine range included. Simulated by refusing such writes, 45 test
cases fail in seven files, each needing another way to swap a tissue group,
inject a failure or move a setting: in unit tests, `test_state_capture.py`
has 14, `test_uptake_system_failure.py` 9 and
`test_agent_simulation_validation.py` 3; in integration tests,
`test_controller.py` has 2 and `test_simulation_view.py` 3; in reference
tests, `test_late_washout_against_published_fits.py` has 12 and
`test_published_wash_in_and_elimination.py` 2. The 24 writes in five `core/`
files, the per-step ones included, become `object.__setattr__(self, ...)`,
against `.claude/rules/core-domain.md`'s bar that the code read like the
domain.

**Accept the window and record it.** No code: `docs/MODEL.md` and the module
docstring of `core/supported_ranges.py` name the assignment as a way in that
the next settings build refuses. It leaves the Reset path above as it is.

**Recommended.** The `__setattr__` guard. It is `PL-0YYV`'s own rule, refuse a
bare `float` where a flow is stored for the callers `mypy` does not read,
applied to the one place a flow is stored that it missed, for no measurable
cost and four test edits, and it closes the Reset path with it, since no field
can then hold a bare `float`. Freezing buys the setter-held checks as well,
but the dial's is moving onto the settings record in `PL-BBMG` (P1, ready),
after which a dial written past the maximum is refused at the next step as a
flow is today, and the machine range binds nothing while no profile declares
one: 45 test rewrites and an `object.__setattr__` on every per-step write is
too much to pay for those. Accepting leaves a notebook one assignment from a
paused run reading a flow a hundred times the supported maximum with no
notice, where `CLAUDE.md`'s standard puts an obvious failure first.

**Done when.** Assigning a bare `float` to
`BreathingCircuit.fresh_gas_flow_l_min`,
`AlveolarCompartment.alveolar_ventilation_l_min` or
`PatientCompartments.cardiac_output_l_min` raises the `TypeError` its
`require_*` raises, at the assignment, and leaves the field holding what it
held, so `SimulationController.snapshot()` cannot copy a flow that was not
built as its type and the reproduction above stops at its assignment;
`tests/unit/test_state_capture.py` perturbs a flow field with a value built as
its type; `docs/MODEL.md` § "Supported input ranges" and the module docstring
of `core/supported_ranges.py` count the assignment among the ways a flow gets
in; and a test in `tests/unit/test_supported_ranges.py` named
`test_a_bare_float_written_onto_a_compartment_is_refused_at_the_write` pins it
for all three flows. A dial written past the vaporizer maximum stays
`PL-BBMG`'s.
