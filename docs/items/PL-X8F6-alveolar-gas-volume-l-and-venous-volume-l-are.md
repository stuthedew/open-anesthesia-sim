---
id: PL-X8F6
title: Alveolar gas_volume_l and venous volume_l are guarded positive-finite in __post_init__, and no compartment-level test asserts either rejection
priority: P2
effort: S
status: ready
classes: test
feature: invariant-test-gaps
touches: tests/unit/test_alveolar.py, tests/unit/test_blood.py
added: 2026-09-19
verify: grep -q 'def test_rejects_invalid_gas_volume' tests/unit/test_alveolar.py && grep -q 'def test_rejects_invalid_venous_volume' tests/unit/test_blood.py
---

**Problem.** Alveolar gas_volume_l and venous volume_l are guarded positive-finite in __post_init__, and no compartment-level test asserts either rejection

**Where.** `src/anesthesia_sim/core/alveolar.py:70`, which calls
`require_positive_finite` on `gas_volume_l`, and
`src/anesthesia_sim/core/blood.py:41`, which calls it on `volume_l`, both in
`__post_init__`. No test in `tests/unit/test_alveolar.py` or
`tests/unit/test_blood.py` constructs the compartment with a zero, negative or
non-finite volume and asserts the rejection; the two volumes are refused only
one level up, by `test_rejects_a_parameter_set_that_could_not_describe_a_patient`
in `tests/unit/test_governing_equations.py`.

**Why it matters.** "All volumes are finite and positive" is the first
required invariant, and the circuit and tissue compartments each have a
compartment-level rejection test (`test_rejects_invalid_circuit_volume` in
`tests/unit/test_circuit.py`, `test_rejects_invalid_tissue_volume` in
`tests/unit/test_tissue.py`); these two do not, so a guard removed from either
`__post_init__` is caught only while the settings-level test still routes
through it. Found 2026-09-19 by `PL-4FBP`'s measurement.

**Done when.** `tests/unit/test_alveolar.py` and `tests/unit/test_blood.py`
each reject a zero, a negative and a non-finite volume at construction, in
the shape the circuit and tissue tests already use, and the annotation pass
(`PL-8LDF`) can name them beside the first invariant.
