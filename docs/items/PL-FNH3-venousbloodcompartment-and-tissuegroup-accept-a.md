---
id: PL-FNH3
title: VenousBloodCompartment and TissueGroup accept a volume and partition coefficient whose product overflows capacity_l to inf, so the venous pool's advance stores nan (an equilibrium of inf * 0.0) rather than refusing at build, and the pool accepts nan written straight onto agent_amount_l; the tissue refuses the nan at its __setattr__ (found reviewing PL-XWFP)
priority: P2
effort: S
status: done
classes: defect
feature: parse-dont-validate
milestone: v0.6.0
touches: src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/tissue.py, tests/unit/test_blood.py, tests/unit/test_tissue.py, src/anesthesia_sim/core/validation.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
closed: 2026-10-19
pr: 1676
payoff: a venous pool or tissue group whose capacity overflows is refused when it is built, naming the factor, instead of storing nan and passing it on to every fraction read from it
verify: grep -q 'def test_a_capacity_that_overflows_is_refused_at_build' tests/unit/test_blood.py && grep -q 'def test_a_capacity_that_overflows_is_refused_at_build' tests/unit/test_tissue.py
---

**Problem.** VenousBloodCompartment and TissueGroup accept a volume and partition coefficient whose product overflows capacity_l to inf, so the venous pool's advance stores nan (an equilibrium of inf * 0.0) rather than refusing at build, and the pool accepts nan written straight onto agent_amount_l; the tissue refuses the nan at its __setattr__ (found reviewing PL-XWFP)

**Reproduced 2026-10-17** on this tree (`b9b3c812`).
`VenousBloodCompartment(volume_l=1e200, blood_gas_partition_coefficient=1e200,
blood_flow_l_min=5.0)` builds with `capacity_l` of `inf`, and
`advance(Fraction(0.0), 1.0)` returns `nan` and stores `nan` (the equilibrium
`exponential_approach` is handed is `inf * 0.0`). A `TissueGroup` built from
the same factors also builds with an infinite capacity; its `advance` refuses
the `nan` at `__setattr__` ("agent_amount_l must be nonnegative and finite"),
so the tissue fails loudly one step late, at the write rather than the build.
On an ordinary pool (1.0 L, 0.65), `agent_amount_l = float("nan")` is stored
as given, because `VenousBloodCompartment` has no `__setattr__`.

**Unreachable from any shipped input**, which sets the band: every volume and
coefficient comes from `data/patients/reference_adult.json` and the three
agent files, fixed values (volumes of 1.222 to 33.0 L, coefficients of 0.42
to 70.0), and no
control sets either; overflow needs a product past about 1.8e308. Nor does a
run read these closed forms: `advance()` here is each compartment's own
analytic step, and a run steps through `AgentUptakeSystem.advance()`.

**Split with `PL-19Y0`.** The `nan` written straight onto the pool's
`agent_amount_l` is a direct write to a checked field, which `PL-19Y0` (in
flight on `claude/gate2-product-batch-carry-h81gwd`) holds to its
constructor's checks; it is that item's, and is not repeated here. `PL-19Y0`'s
brief also records, as a fact for its fix, that "an infinite capacity built
from finite factors (1e200 by 1e200) passes construction and admits any
amount", without making the build refuse it. That half is this item.

**Why it matters.** `CLAUDE.md`'s standard prefers an obvious failure to a
plausible or poisoned value: a capacity of `inf` is a compartment no equation
in `docs/MODEL.md` describes, and the pool turns it into a stored `nan` that
every fraction read from it then carries, where refusing at the build names
the factor that made it.

**Done when.** `VenousBloodCompartment.__post_init__` and
`TissueGroup.__post_init__` refuse a `capacity_l` that is not finite with a
`SimulationConfigurationError` naming both factors, so neither compartment can
be built holding an infinite capacity and the pool's `advance` can no longer
form an `inf * 0.0` equilibrium. The tissue's `__setattr__` keeps leaving a bad
capacity to `__post_init__` as it does now. Regression tests named
`test_a_capacity_that_overflows_is_refused_at_build` in
`tests/unit/test_blood.py` and `tests/unit/test_tissue.py` replay the 1e200 by
1e200 build above and pin the largest finite product admitted.

**Checked 2026-10-19, and fixed on `claude/core-guard-defects-u39w8s`.** Real
in part on `main` at `6fd84bd5`. Since `PL-19Y0` the venous pool has a
`__setattr__`, so its `advance` now refuses the `nan` at the write rather than
storing it, and a `nan` written straight onto `agent_amount_l` is refused.
The build still admitted an infinite capacity for both compartments. The
checks are made in `__setattr__` rather than `__post_init__`, because since
`PL-19Y0` the constructors make no check of their own: whichever factor is
written second is refused by `require_a_capacity`, which also holds a volume
rewritten onto a built compartment. The largest finite capacity,
`sys.float_info.max`, is admitted.

**Run against the code before the fix, 2026-10-19:** `git checkout origin/main -- src/anesthesia_sim/core` and then `uv run pytest -q -p no:randomly tests/unit/test_tissue.py tests/unit/test_blood.py tests/unit/test_parameters.py -k "overflows or however_it_is_built"` failed all three selected tests with `Failed: DID NOT RAISE SimulationConfigurationError`.
