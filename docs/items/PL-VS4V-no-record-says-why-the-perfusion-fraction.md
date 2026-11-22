---
id: PL-VS4V
title: No record says why the perfusion-fraction allowance is 1e-12 or the cardiac-output allowance is one part in 10**9: core/rounding.py states both values, what each is measured against and how far above rounding each sits, but git log -S traces them only to v0.1.0 (875ba085) and to the matrix-exponential change (d8deea50), neither of which gives a reason
priority: P1
effort: S
status: ready
classes: safety
feature: numbers-outside-their-valid-range
touches: src/anesthesia_sim/core/rounding.py, tests/unit/test_rounding.py
deferred-from: v0.7.0 - not live: checked 2026-11-22 at d4e8200c: test_rounding.py holds FLOW_FRACTION_TOLERANCE between four machine epsilons and the 0.002 error of De Wolf's printed fractions, which the loader refuses, and the cardiac-output allowance of one part in 10**9 is far below any transcription error, so no learner can see a wrong value now
added: 2026-11-11
payoff: The checks that accept a patient's tissue flows rest on allowances whose size has a stated, tested reason.
---

**Problem.** No record says why the perfusion-fraction allowance is 1e-12 or the cardiac-output allowance is one part in 10**9: core/rounding.py states both values, what each is measured against and how far above rounding each sits, but git log -S traces them only to v0.1.0 (875ba085) and to the matrix-exponential change (d8deea50), neither of which gives a reason

**Checked 2026-11-22**, at `d4e8200c`. The docstring of `FLOW_FRACTION_TOLERANCE` in `src/anesthesia_sim/core/rounding.py` still ends "no record says why it is 1e-12 and not another number between those two", and that of `CARDIAC_OUTPUT_RELATIVE_TOLERANCE` ends "no record says why it is 1e-9". `test_rounding.py` holds the first allowance between its two edges: it asserts that the allowance is above four times the machine epsilon and below the 0.002 error of the fractions De Wolf et al. print.

**Why it matters.** Both allowances decide whether a patient's tissue flows are accepted. One that is too wide would let a transcribed perfusion fraction or a wrong set of flows through, and one that is too tight would refuse a correct set. The safety standard asks that a constant behind such a check be traceable to its reason, and a later session cannot tell whether either value may move.

**Done when.** Each of the two docstrings gives a reason that a record holds, or each value is replaced by one derived from the rounding bounds that `core/rounding.py` already states. A test shows that each allowance lies above the rounding a correct set of flows carries and below the smallest transcription error the loader must refuse, and neither docstring still says that no record gives the reason.

**Generator check.** An instance of the fact that `PL-GJ1W` (no one place states how far a computed value can be from the exact one) names: how far a computed value can be from the exact one, and so what a comparison on it proves. `#2121` gathered both allowances into `core/rounding.py` but could not derive them. That head is still open, so this is not a re-entry.
