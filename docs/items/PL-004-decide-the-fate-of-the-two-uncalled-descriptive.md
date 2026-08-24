---
id: PL-004
title: Decide the fate of the two uncalled descriptive time constants
priority: P2
effort: S
status: needs-decision
classes: defect, refactor
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/simulation.py, tests/unit/test_alveolar.py
added: 2026-08-23
---

**Problem.** Two correct but uncalled quantities sit in the core.
`SimulationSnapshot.circuit_time_constant_s` is computed on every snapshot
but has had no display widget since the v0.1.0 UI rewrite.
`AlveolarCompartment.time_constant_s` — \(60 V_A / \dot{V}_A\), 37.5 s at
the reference adult — lost its only consumer when PL-022 deleted
`advance_ventilation`. Both are unit-tested; neither is read by shipped
code, and `docs/MODEL.md` defines neither.
**Why it matters.** Neither is merely dead. Each is a single-mechanism time
constant that is *not* the time constant of the shipped coupled dynamics:
the circuit one excludes patient uptake, the alveolar one excludes circuit
coupling and blood uptake. A future caller displaying either as "the time
constant" would present a plausible number for the wrong quantity, and a
computed-but-unshown value invites a reader to assume it is trusted output.
**Where.** `core/simulation.py`, `core/alveolar.py`,
`app/simulation_view.py`, `tests/unit/test_alveolar.py`.
**Decision needed.** Whether an uncalled but correct descriptive quantity
earns its place on the core API. Deleting removes the misinterpretation
risk and costs the loader nothing; keeping costs a few lines and preserves
quantities a future display may want. One question asked twice — answer it
once, for both.
**Done when.** Each value is gone with its tests updated, or its docstring
names the mechanism it describes and says it is not the coupled time
constant; any restored display carries an unambiguous label and unit.
