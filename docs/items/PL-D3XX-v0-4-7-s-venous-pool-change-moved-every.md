---
id: PL-D3XX
title: v0.4.7's venous pool change moved every measured residual in tests/reference/test_coupled_dynamics.py and none of the file's documented measurement tables were re-derived
priority: P2
effort: S
status: done
classes: test, docs
feature: numerical-domain
touches: tests/reference/test_coupled_dynamics.py
verify: grep -q "7.1637e-14 muscle" tests/reference/test_coupled_dynamics.py && ! grep -q "5.1919e-14 muscle" tests/reference/test_coupled_dynamics.py && ! grep -q "nine to sixty-seven fold" tests/reference/test_coupled_dynamics.py
added: 2026-09-07
closed: 2026-09-07
---

**Problem.** `PL-8ZJQ`/`PL-BD94` (#423, in v0.4.7) replaced
`venous_blood_volume_l` = 1.0 L with `venous_pool_volume_l` = 1.222 L. That
moves V_v/Q from 12.0 s to 14.7 s, so every state trajectory moves, and with
them every floating-point residual `tests/reference/test_coupled_dynamics.py`
publishes in its derivations. None was re-measured. Isolated by holding
`ORACLE_STEP_S` at its then-current 0.05 s and re-running: the change is the
model's, not the oracle's.

    HELD_RUN_ROUNDING_BOUND's table   documented 2026-09-06   measured 2026-09-07
    sevoflurane  3600 s               1.3850e-14 muscle       1.4764e-14 muscle
    isoflurane   3600 s               5.1919e-14 muscle       1.8093e-14 muscle
    desflurane   3600 s               4.8562e-14 muscle       7.2036e-14 muscle

**Why it matters.** Nothing fails and no bound is violated — `1e-12` still
holds — but the stated derivations no longer describe the arithmetic they
claim to. The bound's "allows 19.3 times it" is 13.9x, its subdivision spread
of 3.1675e-13 is 2.1696e-13, and the worst agent has moved from isoflurane to
desflurane. A reader tightening either bound, or citing one as evidence of the
solver's accuracy, reasons from figures that no longer hold. This file's
comments are the audit trail for two safety-critical numerical bounds, which is
the standard `CLAUDE.md` sets for traceability rather than tidiness.

The general lesson is the one worth carrying: a parameter revision invalidates
every measured figure downstream of it, and the close-out sweep that catches
prose does not catch a number. `PL-ZVS7`-style reference gates re-derive on
each run; a figure quoted in a comment does not.

**Where.** `tests/reference/test_coupled_dynamics.py` — `HELD_RUN_ROUNDING_BOUND`'s
derivation table and margins, `EXACT_STEP_ORACLE_TOLERANCE`'s table, the module
header's growth ratios, and `_envelope_corner_held`'s worst-residual claim.

**Done when.** Every quoted figure is re-measured against the shipped model and
the stated margins recomputed, or the figure is removed as not worth
maintaining.

**Found.** `PL-B1WW`, 2026-09-07, while re-measuring the same file for the
oracle refinement.

**Done, 2026-09-07, riding `PL-B1WW`'s commit** (`PL-CP74`: it took no commit
of its own). Re-measured at the reference operating point, endpoint of each
horizon, worst over the six fractions, under the refined oracle:

                    60 s                600 s                   3600 s
    sevoflurane     5.6899e-16 circuit  2.7131e-15 circuit      1.5056e-14 muscle
    isoflurane      2.4633e-16 circuit  3.9864e-15 vessel rich  1.8395e-14 muscle
    desflurane      3.5041e-16 circuit  1.3427e-14 vessel rich  7.1637e-14 muscle

`HELD_RUN_ROUNDING_BOUND` holds unchanged at `1e-12`: it now allows 14.0x the
worst residual and clears the re-measured subdivision spread of 2.1696e-13 by
4.6x. Also corrected: the module header's "nine to sixty-seven fold" growth
ratios, which were taken against 60 s residuals of a few units in the last
place and reported how few bits had accumulated by 60 s rather than anything
about the step. The absolute table replaces them and the file now says why the
ratio is not quoted.
