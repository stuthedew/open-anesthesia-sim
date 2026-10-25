---
id: PL-6YKY
title: Field guards in core/ match a field's name as a string (circuit.py's __setattr__ tests name == "circuit_volume_l", blood.py and tissue.py test name == "volume_l"), so renaming the field leaves its validation keyed to a name nothing sets any more and the check stops running without an error
priority: P1
effort: S
status: ready
classes: safety, defect
feature: one-source-of-truth
touches: tests/unit/test_field_guards.py
added: 2026-10-25
payoff: a field guard in core/ cannot stop running because its field was renamed
verify: grep -q 'def test_every_name_a_core_field_guard_compares_with_is_a_field' tests/unit/test_field_guards.py
---

**Problem.** Field guards in core/ match a field's name as a string (circuit.py's __setattr__ tests name == "circuit_volume_l", blood.py and tissue.py test name == "volume_l"), so renaming the field leaves its validation keyed to a name nothing sets any more and the check stops running without an error

**Found 2026-10-25** on `main` at `9966ca3b`, while counting the 12 unit-like strings for `PL-G84G`. Seven modules in `core/` validate a field when it is written, in a `__setattr__` that compares the field's name with a string: `alveolar.py`, `blood.py`, `circuit.py`, `patient.py`, `simulation.py` and `tissue.py`, 22 comparisons in all (`grep -n 'if name == "' src/anesthesia_sim/core/*.py`, plus the `elif` lines). Each string is a second copy of the field's name, which the dataclass already declares.

**Why it matters.** If a field is renamed and its string is not, the guard's branch never matches again. The field then accepts any value, including a negative volume or a concentration above the vaporizer's maximum, and nothing raises. A test that writes an invalid value under the new name would catch it, but only where such a test exists for that field. This is a refusal on a safety-critical path that could stop running without an error.

**Recommendation.** Keep the guards as they are, and add one test that reads each guarded class's `__setattr__` and checks that every name it compares with is a field of that class. That makes the next drift fail without restructuring seven modules. Replacing the string comparisons with a table keyed by field was considered; it would still key the table by name, so it moves the copy rather than removing it.

**Done when.** A test under `tests/unit/` fails when a guard in `core/` compares with a name that is not a field of its class, and passes on the current tree. A deliberately misspelt guard name, tried once by hand, makes it fail.
