---
id: PL-5GVL
title: A FreshGasFlow written straight onto BreathingCircuit.fresh_gas_flow_l_min past set_fresh_gas_flow is held to its type alone by __setattr__ (PL-LBQY), so one outside the machine's deliverable_fresh_gas_flow_range is admitted where the constructor and the setter refuse it through _require_deliverable_flow; it binds nothing while no shipped profile declares a range, and is the flow side of the range guard PL-19Y0 folded in from PL-HJ7L (found in PL-KFNP's design round)
priority: P2
effort: S
status: ready
classes: defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/circuit.py, tests/unit/test_circuit.py, docs/MODEL.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
payoff: once any machine profile declares a deliverable flow range, a flow that machine cannot set can no longer be written onto the circuit and run, charted and shown as if accepted
verify: grep -q 'def test_a_flow_written_past_the_setter_is_held_to_the_machines_range' tests/unit/test_circuit.py
---

**Problem.** A FreshGasFlow written straight onto BreathingCircuit.fresh_gas_flow_l_min past set_fresh_gas_flow is held to its type alone by __setattr__ (PL-LBQY), so one outside the machine's deliverable_fresh_gas_flow_range is admitted where the constructor and the setter refuse it through _require_deliverable_flow; it binds nothing while no shipped profile declares a range, and is the flow side of the range guard PL-19Y0 folded in from PL-HJ7L (found in PL-KFNP's design round)

**Reproduced 2026-10-17** on this tree (`b9b3c812`), with
`DeliverableFreshGasFlowRange(1.0, 5.0)`: `BreathingCircuit(fresh_gas_flow_l_min
=FreshGasFlow(8.0), deliverable_fresh_gas_flow_range=...)` and
`set_fresh_gas_flow(FreshGasFlow(8.0))` each raise
`SimulationConfigurationError`, while `circuit.fresh_gas_flow_l_min =
FreshGasFlow(8.0)` on the same circuit is accepted and leaves 8.0 L/min held
beside an `accepted_fresh_gas_flow_range_l_min` of `(1.0, 5.0)`. The
`__setattr__` docstring says so on purpose ("The machine's range is not checked
here: it is a relation the setter and the constructor hold"), and
`docs/MODEL.md` § "Supported input ranges" repeats it ("The type is all the
write checks of a flow"). `PL-LBQY`'s design round measured the same gap and
left it, because no profile declared a range then.

**Unreachable from any shipped input**, which sets the band:
`data/machines/reference_circle_system.json`, the one shipped profile, stores
`deliverable_fresh_gas_flow_range: null`, so `_require_deliverable_flow`
returns at once for every circuit a run builds, and nothing under `src/` writes
the field but `set_fresh_gas_flow`. It binds the day `PL-TBMK` (a second
machine profile) or any profile declares a range.

**Not `PL-19Y0` filed again, but its neighbour.** `PL-19Y0` holds every checked
field of the five records to what its constructor refuses and has folded in
the *range* field's rewrite (from `PL-HJ7L`); its scan counted the three flows
as already guarded, by type, so this, the *flow's* write against the range,
sits outside the list it walked. `PL-KFNP`'s design round names it as such.
`PL-19Y0` is claimed on `claude/gate2-product-batch-carry-h81gwd` (claim only,
2026-10-17), so this stays its own item rather than a fold that branch would
not see; where that branch's guard already refuses this write, close this
under its pull request.

**Why it matters.** A flow outside the mounted machine's range is a value the
interface's control can never offer (`PL-7CRY` bounds the slider by
`accepted_fresh_gas_flow_range_l_min`), so once a profile declares one, a
notebook or test that writes the field directly runs, snapshots and charts a
flow the machine cannot set, under readouts that say nothing was refused.

**Done when.** A `FreshGasFlow` assigned to
`BreathingCircuit.fresh_gas_flow_l_min` outside a declared
`deliverable_fresh_gas_flow_range` is refused at the assignment with the
`SimulationConfigurationError` `_require_deliverable_flow` raises, and the
field holds what it held. The constructor's own first write is still admitted
on its type (the dataclass writes the flow before the range field exists;
`PL-KFNP`'s "is this a rewrite" condition, `hasattr` on the slot, is the
precedent) with `__post_init__`'s check left to refuse it, so construction,
`dataclasses.replace`, copy and pickle behave as now. The `__setattr__`
docstring and `docs/MODEL.md` § "Supported input ranges" say the write meets
the machine's range. `test_a_flow_written_past_the_setter_is_held_to_the_machines_range`
in `tests/unit/test_circuit.py` pins the refusal, the unchanged field, an
in-range rewrite admitted, and a circuit with no declared range unaffected.
