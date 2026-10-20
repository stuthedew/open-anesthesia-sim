---
id: PL-8LQZ
title: A TissueGroup whose volume and tissue:gas coefficient multiply to a capacity that underflows to 0.0 (1e-200 x 1e-200) passes construction and require_room_for_the_agent_held, and partial_pressure_fraction then raises ZeroDivisionError rather than a refusal: the mirror of PL-FNH3's capacity overflowing to inf (found reviewing PL-19Y0)
priority: P2
effort: S
status: done
classes: defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, tests/unit/test_tissue.py, tests/unit/test_blood.py, src/anesthesia_sim/core/validation.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
closed: 2026-10-19
pr: 1676
payoff: a compartment whose capacity underflows to zero is refused at build by name, instead of failing later with a bare division error the halt path does not handle
verify: grep -q 'build(1e-200, 1e-200)' tests/unit/test_tissue.py && grep -q 'volume_l=1e-200, blood_gas_partition_coefficient=1e-200' tests/unit/test_blood.py
reenters: PL-ZGYX
---

**Problem.** A TissueGroup whose volume and tissue:gas coefficient multiply to a capacity that underflows to 0.0 (1e-200 x 1e-200) passes construction and require_room_for_the_agent_held, and partial_pressure_fraction then raises ZeroDivisionError rather than a refusal: the mirror of PL-FNH3's capacity overflowing to inf (found reviewing PL-19Y0)

**Reproduced 2026-10-17.** `TissueGroup(name='x', volume_l=1e-200,
perfusion_fraction=0.1, blood_gas_partition_coefficient=1.0,
tissue_gas_partition_coefficient=1e-200)` builds with `capacity_l == 0.0`, and
`partial_pressure_fraction` then raises `ZeroDivisionError: division by zero`.

**Why it matters.** The core's contract is that an invalid record is refused at
build, by name, with a `SimulationConfigurationError`. A `ZeroDivisionError` at
the first read is an obvious failure rather than a wrong number, but it names
nothing, and it escapes the handlers that turn a refusal into a halt. No shipped
data reaches it.

**Done when.** A tissue group, and the venous pool if it shares the defect, whose
capacity is not a positive finite number is refused at build with a message
naming both factors. A test pins the refusal. `PL-FNH3` is the overflow half and
can be done in the same change.

**Generator check.** An instance of `PL-ZGYX`'s fact, filed after that head
closed on 2026-10-11.

**Checked 2026-10-19, and fixed on `claude/core-guard-defects-u39w8s`.** Still
real on `main` at `6fd84bd5`, for the venous pool as well as the tissue group:
both built from 1e-200 by 1e-200 and raised `ZeroDivisionError` on the first
read. The fix is `PL-FNH3`'s: `core/validation.py`'s `require_a_capacity`,
called as either factor is written once the other is held, refuses a product
that is zero or not finite and names both factors. The regression cases sit
in `test_a_capacity_that_overflows_is_refused_at_build` in
`tests/unit/test_tissue.py` and `tests/unit/test_blood.py`, beside the
overflow, so the `verify:` greps those cases rather than a test of its own.

**Run against the code before the fix, 2026-10-19:** `git checkout origin/main -- src/anesthesia_sim/core` and then `uv run pytest -q -p no:randomly tests/unit/test_tissue.py tests/unit/test_blood.py tests/unit/test_parameters.py -k "overflows or however_it_is_built"` failed all three selected tests with `Failed: DID NOT RAISE SimulationConfigurationError`.
