---
id: PL-GZP6
title: Two of docs/MODEL.md's required tests are not implemented
priority: P2
effort: S
status: done
classes: defect, test
feature: model-spec-accuracy
touches: tests/unit/test_tissue.py, tests/reference/test_sevo_patient.py
added: 2026-09-03
closed: 2026-09-07
verify: uv run pytest tests/unit/test_tissue.py tests/reference/test_sevo_patient.py && grep -q 'def test_a_larger_or_more_soluble_tissue_has_a_longer_time_constant' tests/unit/test_tissue.py && grep -q 'def test_washout_never_increases_total_system_mass' tests/reference/test_sevo_patient.py
---

**Problem.** `docs/MODEL.md` § "Required tests" lists fifteen tests the
implementation must carry. Thirteen exist. Two do not:

- § "Directional tissue-capacity test" (`docs/MODEL.md:975`): *"Increasing
  either V_i or lambda_i:b, with flow held constant, must lengthen the tissue
  time constant."* No test compares two tissue time constants. Grepped
  2026-09-03: `time_constant_s` appears in `tests/` eight times, every one of
  them a single-value assertion or a step size passed to `advance()`.
  `test_one_time_constant_reaches_expected_fraction` checks the exponential at
  t = tau and `test_derives_tissue_blood_partition_coefficient` checks a ratio;
  neither is the directional claim.
- § "Washout test" (`docs/MODEL.md:984`): *"setting F_D = 0 must produce
  finite, nonnegative washout without spontaneous increases in total system
  mass."* Nothing asserts total stored mass is non-increasing while the dial is
  at zero. `test_long_wash_in_and_washout_validate_agent_simulation` checks the
  accounting identity, which holds by construction whatever the transfer rates
  are, and `test_extreme_ui_slider_range_stays_valid_through_wash_in_and_washout`
  checks finiteness, range, and that the circuit fraction fell.

**Why it matters.** Both invariants are believed to hold - the tissue time
constant is `60 * V_i * lambda_i:b / Q_i` by inspection, and mass cannot
spontaneously increase because every internal transfer is applied as an
equal-and-opposite pair. So this is a gap in the gate rather than a wrong
value, and it is P2 rather than P1 for that reason. What it costs is that a
specification saying "must" is satisfied by nobody: a later change to the
tissue equation that inverted the capacity dependence, or one that let the
exhaust term reverse sign during washout, would be caught by the oracle in
`tests/reference/test_coupled_dynamics.py` only if it happened to exceed the
splitting bound, and by nothing that names the invariant it broke.

The washout half also carries the more useful diagnostic. Mass balance says
"agent is unaccounted for"; "total stored mass rose while the vaporizer was
off" says which direction and when.

**Where.** `docs/MODEL.md:971-990`; `tests/unit/test_tissue.py`;
`tests/reference/test_sevo_patient.py`.

**Approach.** Two tests, both small:

1. In `tests/unit/test_tissue.py`, build three otherwise identical tissue
   groups and assert `time_constant_s` rises with `volume_l` and with
   `tissue_gas_partition_coefficient`, at fixed `blood_flow_l_min`. State the
   MODEL.md section in the docstring, as the other required tests do.
2. In `tests/reference/test_sevo_patient.py`, load the system, set the dial to
   zero, and assert `total_stored_agent_l` is non-increasing across every step
   of the washout. Sample every step rather than the endpoints - the claim is
   about spontaneous increases, which an endpoint comparison cannot see. Note
   in the docstring that individual tissue fractions may rise through
   redistribution, which MODEL.md explicitly permits and this test must not
   forbid.

**Related.** `PL-2M9N` builds the check that would have found this, and would
have found it the day the section was written rather than in an audit. Doing
that one first is cheaper only if this one is folded into it; they are filed
separately because the two missing tests are worth having whether or not the
binding is ever built.

**Done when.** Both tests exist, name their MODEL.md section, and fail if the
invariant they state is broken.
