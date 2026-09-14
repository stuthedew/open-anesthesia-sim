---
id: PL-DJYF
title: AlveolarCompartment restates the reference patient's gas volume 2.5 and ventilation 4.0 as core/ dataclass defaults, the same restatement PL-4YY1 found on BreathingCircuit
priority: P1
effort: S
status: done
classes: defect, science, docs
feature: model-spec-accuracy
milestone: v0.4.22
touches: src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/parameters.py, docs/MODEL.md, tests/unit/test_alveolar.py
added: 2026-09-13
closed: 2026-09-13
pr: 550
verify: uv run pytest tests/unit/test_alveolar.py && grep -q 'def test_the_bare_alveolar_defaults_match_the_shipped_patient_file' tests/unit/test_alveolar.py
---

**Problem.** AlveolarCompartment restates the reference patient's gas volume 2.5 and ventilation 4.0 as core/ dataclass defaults, the same restatement PL-4YY1 found on BreathingCircuit
**Why it matters.** Verified 2026-09-13. `src/anesthesia_sim/core/alveolar.py`
lines 42-43 carry `gas_volume_l: float = 2.5` and `alveolar_ventilation_l_min:
float = 4.0` as dataclass field defaults. Both values already have a sourced
home: `src/anesthesia_sim/data/patients/reference_adult.json` stores
`alveolar_gas_volume_l: 2.5` and `default_alveolar_ventilation_l_min: 4.0`, each
with a provenance entry recording that the figure is tier 3 and unadopted. So
this is not a missing citation - it is the same scientific constant written in
two places, one of which is cited and one of which is not, with nothing holding
them equal. No test pins the alveolar defaults: `PL-4YY1` left
`test_the_bare_circuit_defaults_match_the_shipped_machine_file` behind for the
breathing circuit and nothing equivalent exists here.

A constant that can drift from the parameter set `docs/MODEL.md` cites is a
simulation running on a value the specification does not name, presented with
provenance that looks correct. That is the failure `CLAUDE.md`'s provenance rule
exists to prevent, and it is why this is seated where its twin was rather than
by a fresh judgment: `PL-4YY1` (record provenance for the circuit volume and
default fresh gas flow) closed at P1, effort S, `defect, science, docs`,
`feature: model-spec-accuracy`, shipped in v0.4.20.

**Done when.** `AlveolarCompartment` no longer restates either constant, or - if
a bare default is wanted so the dataclass stays constructible - a test in
`tests/unit/test_alveolar.py` pins both against
`src/anesthesia_sim/data/patients/reference_adult.json` the way `PL-4YY1` pinned
the circuit's, and `docs/MODEL.md` says which file is the single authority for
each. Either way the value exists in one place that a reader can find from the
provenance table.
