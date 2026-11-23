---
id: PL-VS4V
title: No record says why the perfusion-fraction allowance is 1e-12 or the cardiac-output allowance is one part in 10**9: core/rounding.py states both values, what each is measured against and how far above rounding each sits, but git log -S traces them only to v0.1.0 (875ba085) and to the matrix-exponential change (d8deea50), neither of which gives a reason
priority: P1
effort: S
status: done
classes: safety
feature: floating-point-domain
touches: src/anesthesia_sim/core/rounding.py, tests/unit/test_rounding.py, tests/unit/test_governing_equations.py
deferred-from: v0.7.0 - not live: checked 2026-11-22 at d4e8200c: test_rounding.py holds FLOW_FRACTION_TOLERANCE between four machine epsilons and the 0.002 error of De Wolf's printed fractions, which the loader refuses, and the cardiac-output allowance of one part in 10**9 is far below any transcription error, so no learner can see a wrong value now
added: 2026-11-11
closed: 2026-11-23
pr: 2314
payoff: The checks that accept a patient's tissue flows rest on allowances whose size has a stated, tested reason.
tests: tests/unit/test_rounding.py::test_the_perfusion_allowance_is_below_the_cardiac_output_allowance_by_more_than_rounding, tests/unit/test_rounding.py::test_the_cardiac_output_allowance_creates_less_agent_than_the_propagator_bound_assumes, tests/unit/test_governing_equations.py::test_flows_from_fractions_at_the_edge_of_the_perfusion_allowance_are_accepted
---

**Problem.** No record says why the perfusion-fraction allowance is 1e-12 or the cardiac-output allowance is one part in 10**9: core/rounding.py states both values, what each is measured against and how far above rounding each sits, but git log -S traces them only to v0.1.0 (875ba085) and to the matrix-exponential change (d8deea50), neither of which gives a reason

**Checked 2026-11-22**, at `d4e8200c`. The docstring of `FLOW_FRACTION_TOLERANCE` in `src/anesthesia_sim/core/rounding.py` still ends "no record says why it is 1e-12 and not another number between those two", and that of `CARDIAC_OUTPUT_RELATIVE_TOLERANCE` ends "no record says why it is 1e-9". `test_rounding.py` holds the first allowance between its two edges: it asserts that the allowance is above four times the machine epsilon and below the 0.002 error of the fractions De Wolf et al. print.

**Why it matters.** Both allowances decide whether a patient's tissue flows are accepted. One that is too wide would let a transcribed perfusion fraction or a wrong set of flows through, and one that is too tight would refuse a correct set. The safety standard asks that a constant behind such a check be traceable to its reason, and a later session cannot tell whether either value may move.

**Done when.** Each of the two docstrings gives a reason that a record holds, or each value is replaced by one derived from the rounding bounds that `core/rounding.py` already states. A test shows that each allowance lies above the rounding a correct set of flows carries and below the smallest transcription error the loader must refuse, and neither docstring still says that no record gives the reason.

**Generator check.** An instance of the fact that `PL-GJ1W` (no one place states how far a computed value can be from the exact one) names: how far a computed value can be from the exact one, and so what a comparison on it proves. `#2121` gathered both allowances into `core/rounding.py` but could not derive them. That head is still open, so this is not a re-entry.

**Done 2026-11-23.** Neither value moved. Each docstring now gives the two
edges its value must lie between, each taken from a record the module or its
tests already hold, and says that the commit that set the number gives no
reason for that point within the edges. `tests/unit/test_rounding.py` holds
each value between its edges.

1. `FLOW_FRACTION_TOLERANCE` must be above the rounding of a correct set, a
   few `MACHINE_EPSILON`, which the existing test checks. It must be below
   `CARDIAC_OUTPUT_RELATIVE_TOLERANCE` less a few roundings, so that every
   fraction set the loader accepts gives flows the settings accept. The new
   `test_the_perfusion_allowance_is_below_the_cardiac_output_allowance_by_more_than_rounding`
   checks that, and the new
   `test_flows_from_fractions_at_the_edge_of_the_perfusion_allowance_are_accepted`
   in `tests/unit/test_governing_equations.py` builds the settings from
   fractions at 99% of the allowance, both sides, at three cardiac outputs.
2. `CARDIAC_OUTPUT_RELATIVE_TOLERANCE` must be above that same edge. Its upper
   edge is the third condition of the derivation in
   `PROPAGATOR_ROUNDING_UNITS`: excess tissue flow creates agent in the venous
   pool, which must stay below 2**-9 of the state over one interval. At
   10 L/min, a 0.01 L pool and 24 h, that caps the allowance at 1.35e-9. The new
   `test_the_cardiac_output_allowance_creates_less_agent_than_the_propagator_bound_assumes`
   computes the condition and the cap from `MAXIMUM_CARDIAC_OUTPUT_L_MIN`,
   `MINIMUM_VOLUME_L` and `MAXIMUM_ELAPSED_SIMULATION_TIME_S`. No test checked
   that condition before. The 2**-9 that the bound's derivation in the test
   file assumes is now one named constant there, read by both.

A finding on the way: the fixed part, `CARDIAC_OUTPUT_TOLERANCE_L_S` (1e-12
L/s), would on its own admit every correct set in the supported range,
because 1e-12 of 10 L/min is 1.7e-13 L/s. The docstring says so.

Checked by hand: with `FLOW_FRACTION_TOLERANCE` set to 1e-8, seven of the
thirteen selected tests fail. With `CARDIAC_OUTPUT_RELATIVE_TOLERANCE` at 2e-9
the propagator-condition test fails, and at 1e-13 the edge test fails.

Docs checked: `docs/VERIFICATION.md` § "Tissue groups and compartment
capacities in the code" and `docs/PARAMETERS.md`'s paragraph on the two
perfusion checks name the constant and its value only, and stay true.
`docs/MODEL.md` § "Blood flow to the tissue groups" gives the perfusion value
in words, one part in a million million, and stays true.

**Review, 2026-11-23.** Both blind review passes found nothing to report.
