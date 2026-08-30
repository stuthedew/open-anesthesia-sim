---
id: PL-0MLQ
title: Refuse a setting outside the documented supported input range
status: untriaged
added: 2026-08-30
classes: safety
touches: src/anesthesia_sim/core/respiratory_system.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/patient.py, docs/MODEL.md
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
(\(C_{\max} = 2.29\times10^{-3}\ \mathrm{s^{-1}}\)) and everything derived
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
