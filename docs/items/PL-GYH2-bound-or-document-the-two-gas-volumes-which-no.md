---
id: PL-GYH2
title: Bound or document the two gas volumes, which no supported range covers
priority: P1
effort: S
status: ready
classes: safety
feature: numerical-domain
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py, docs/MODEL.md
added: 2026-09-02
verify: uv run pytest tests/integration/test_controller.py && python3 tools/doc_check.py check && ! grep -q 'def set_circuit_volume' src/anesthesia_sim/app/controller.py && ! grep -q 'PL-GYH2' docs/MODEL.md
---

**Problem.** PL-0MLQ moved the three flow controls into a declared, enforced
input domain (`core/supported_ranges.py`). The two gas volumes were left out
of it and are still guarded only by `require_positive_finite`:
`BreathingCircuit(circuit_volume_l=10_000.0)` and
`AlveolarCompartment(gas_volume_l=1e-6)` are both accepted, and
`SimulationController.set_circuit_volume` is a public setter with no upper
bound that no interface control reaches.

**Why it matters.** Less than the flows did, and the reason is worth
recording rather than assuming. Neither volume is a user control, so no
slider can reach a value outside the verified domain, and every reference
measurement in `docs/MODEL.md` holds both at their data-file values. But the
splitting error depends on both — the circuit-to-alveolar exchange rate is
$`\dot{V}_A(1/V_C + 1/V_A)`$, so a small alveolar volume raises it the way a
large ventilation does — and
`tests/unit/test_uptake_system_failure.py` already builds a 0.005 L lung
precisely because a volume that small breaks the split at a supported step.
That construction is a deliberate test fixture; nothing distinguishes it from
a caller who means it.

**Where.** `core/circuit.py` (`circuit_volume_l`, `set_circuit_volume`),
`core/alveolar.py` (`gas_volume_l`), `app/controller.py:280`
(`SimulationController.set_circuit_volume`), `docs/MODEL.md` § "Supported
input ranges" — which currently states the gap and points here.

**Decided (project owner, 2026-09-02): data-file parameters only.** Neither
volume becomes a control. The question was whether to give them a measured
range like the flows — which would grow the envelope sweep an axis and
re-derive the displayed resolution and supported step over the new domain —
or to establish that the data file is the only way to set them. The second,
for a knob no teaching case has asked for: `SimulationController.set_circuit_volume`
reads as a leftover rather than a half-built feature, and
`tests/reference/test_coupled_dynamics.py` called it "a slider" in a docstring
until PL-0MLQ corrected that. This makes the item `S` rather than `M`.

**Which setter goes, precisely.** `SimulationController.set_circuit_volume`
(`app/controller.py:280`), the app-layer passthrough no interface control
reaches, together with its two callers in
`tests/integration/test_controller.py` (lines 264 and 291).
`BreathingCircuit.set_circuit_volume` (`core/circuit.py:104`) **stays**: the
controller's own constructor path calls it (`app/controller.py:125`), as does
`tests/reference/test_coupled_dynamics.py:632`, so deleting it would break the
route by which the data file's value reaches the circuit at all. The finding
is that the *public, unbounded, interface-level* setter exists, not that the
core method does.

**Done when.** `SimulationController.set_circuit_volume` is gone, both volumes
are established in `docs/MODEL.md` as data-file parameters rather than
controls, and § "Supported input ranges" states that instead of naming this
item as an open gap.

**What v0.4.1 does to this (added 2026-09-03).** The deliverable stands - the two gas
volumes still reach `core/` unbounded through
`SimulationController.set_circuit_volume` - but the *argument* weakens and must
be restated. "The splitting error depends on both" stops being true under
`PL-GS5X`, and `BREAKDOWN_ALVEOLAR_GAS_VOLUME_L = 0.005`
(`tests/unit/test_uptake_system_failure.py`) is currently justified as the
volume "small enough to break the split at a supported step"; an exact
exponential does not break there. The bound is still wanted - a 5 mL alveolus is
not a patient - but on physiological grounds rather than numerical ones. Restate
it that way and the item survives `PL-X9KD` unchanged.

**Central argument void after `PL-GS5X`, 2026-09-06.** The finding rests on
"the splitting error depends on both — the circuit-to-alveolar exchange rate is
$`\dot V_A(1/V_C + 1/V_A)`$". There is no splitting error, and no
circuit-to-alveolar exchange rate as a separate quantity: ventilation is a pair
of entries in the system matrix and the whole system is solved at once.

Whether circuit volume should be a control, and what range it would need, is
untouched — it is a question about the settings envelope and the verification
domain, which `docs/MODEL.md` § "What a setting outside the range costs" now
grounds those on rather than on numerical error. Re-argue on that ground.
