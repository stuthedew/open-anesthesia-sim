---
id: PL-004
title: Decide the fate of the two uncalled descriptive time constants
priority: P2
effort: S
status: done
classes: defect, refactor
feature: core-boundaries
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core/alveolar.py, docs/MODEL.md, docs/WORKING_NOTES.md, tests/unit/test_alveolar.py, tests/unit/test_simulation_view.py
added: 2026-08-23
closed: 2026-09-02
pr: 210
verify: uv run pytest tests/unit/test_alveolar.py tests/unit/test_simulation_view.py && ! grep -q 'def time_constant_s' src/anesthesia_sim/core/alveolar.py && ! grep -q circuit_time_constant_s src/anesthesia_sim/app/controller.py && grep -q 'def time_constant_s' src/anesthesia_sim/core/circuit.py && grep -qF 'not the time constant of the coupled system' docs/MODEL.md
---

**Problem.** Two values are computed and never read.
`SimulationSnapshot.circuit_time_constant_s` (`app/controller.py`, declared
at line 53 and written at line 240) has had no display widget since the
v0.1.0 UI rewrite; its only other mention is a test helper that supplies a
dummy because the dataclass requires the field.
`AlveolarCompartment.time_constant_s` — $`60 V_A / \dot{V}_A`$, 37.5 s at the
reference adult — lost its only consumer when PL-022 deleted
`advance_ventilation`, and `AlveolarCompartment` now has no `advance` at all.
Both are unit-tested; neither is read by shipped code.

This item's original text named `BreathingCircuit.time_constant_s` as the
second uncalled value and stated that `docs/MODEL.md` defines neither. Both
claims were wrong, and the correction is what shaped the decision below: that
property is the analytic integrator's own constant, read twice inside
`advance()` (`core/circuit.py`, lines 182 and 194), relied on by
`tests/reference/test_circuit_wash_in.py`, and documented as $`\tau_C`$ in
`docs/MODEL.md` under "Preserved circuit reference tests". It is load-bearing
and is not in scope here.

**Why it matters.** Neither uncalled value is merely dead. Each is a
single-mechanism time constant that is *not* the time constant of the shipped
coupled dynamics: the alveolar one excludes circuit coupling and blood uptake.
A future caller displaying it as "the time constant" would present a plausible
number for the wrong quantity, and a computed-but-unshown value invites a
reader to assume it is trusted output.

**Where.** `core/alveolar.py`, `app/controller.py`, `docs/MODEL.md`,
`tests/unit/test_alveolar.py`, `tests/unit/test_simulation_view.py`.

**Decided.** Delete both, and move the alveolar derivation into
`docs/MODEL.md` as a stated limitation rather than keeping it as callable code
with a warning docstring.

The reasoning is `CLAUDE.md`'s own preference for interfaces that prevent
errors over interfaces that warn after one. A public property on a core
compartment returning a plausible number of seconds is an affordance: it
invites the call, and the person wiring a readout reads the property *name*,
not its prose. A docstring is the weakest available control against exactly
the failure mode this item identifies.

Deleting the code need not delete the knowledge. `docs/MODEL.md` is the
authoritative specification, and an entry recording that the ventilation-only
alveolar turnover is $`60 V_A / \dot{V}_A`$ (37.5 s at reference) *and* that
the shipped coupled system does not relax with that constant — because
alveolar gas exchanges with circuit and blood simultaneously — tells a future
reader strictly more than the docstring did, in the document they consult to
understand the model. What it does not do is hand a caller a one-liner to bind
to a UI label.

Considered and rejected: keep both and document them in place. It preserves
the derivation at the cost of leaving the affordance, and the affordance is
the risk.

**Done when.** `AlveolarCompartment.time_constant_s` and
`SimulationSnapshot.circuit_time_constant_s` are gone, their tests and the
`test_simulation_view.py` helper updated, `BreathingCircuit.time_constant_s`
untouched, and `docs/MODEL.md` records the alveolar turnover as a limitation
naming the mechanism it describes and stating it is not the coupled time
constant.
