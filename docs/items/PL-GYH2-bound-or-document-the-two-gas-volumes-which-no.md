---
id: PL-GYH2
title: Bound or document the two gas volumes, which no supported range covers
priority: P1
effort: M
status: needs-decision
classes: safety
feature: numerical-domain
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/app/controller.py, docs/MODEL.md
added: 2026-09-02
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
`tests/unit/test_respiratory_system_failure.py` already builds a 0.005 L lung
precisely because a volume that small breaks the split at a supported step.
That construction is a deliberate test fixture; nothing distinguishes it from
a caller who means it.

**Where.** `core/circuit.py` (`circuit_volume_l`, `set_circuit_volume`),
`core/alveolar.py` (`gas_volume_l`), `app/controller.py:280`
(`SimulationController.set_circuit_volume`), `docs/MODEL.md` § "Supported
input ranges" — which currently states the gap and points here.

**Decision needed.** Whether either volume should be a *control* at all.
Circuit volume has a controller setter and no slider, which is either a
half-built feature or a leftover; `tests/reference/test_coupled_dynamics.py`
called it "a slider" in a docstring until PL-0MLQ corrected that. If it
becomes a control it needs a measured range like the flows, and the envelope
sweep grows an axis. If it does not, the honest fix may be to drop the
controller setter and let the data file be the only way to set it.

**Done when.** Either both volumes carry a declared range enforced the way
the flows are and `docs/MODEL.md` records the measurement behind it, or the
volumes are established as data-file parameters only — the controller setter
removed or bounded — and `docs/MODEL.md` § "Supported input ranges" says so
instead of naming this item.
