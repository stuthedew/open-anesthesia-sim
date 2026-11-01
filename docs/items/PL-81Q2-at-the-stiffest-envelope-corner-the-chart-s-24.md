---
id: PL-81Q2
title: At the stiffest envelope corner the chart's 24-hour window advances each column by a 1464.4 s propagator that needs 32 squarings, the module's maximum, so each column carries an error of 5.65e-7 and 59 columns accumulate 3.3e-5; decide whether the display path should cap its propagator interval or use a method that avoids over-squaring (Al-Mohy and Higham 2009)
status: untriaged
feature: floating-point-domain
touches: src/anesthesia_sim/core/run_definition.py, src/anesthesia_sim/core/matrix_exponential.py
added: 2026-11-01
---

**Problem.** At the stiffest envelope corner the chart's 24-hour window advances each column by a 1464.4 s propagator that needs 32 squarings, the module's maximum, so each column carries an error of 5.65e-7 and 59 columns accumulate 3.3e-5; decide whether the display path should cap its propagator interval or use a method that avoids over-squaring (Al-Mohy and Higham 2009)

**Measured, 2026-11-01, on `PL-9B1M`'s branch.** The corner has every volume
at 0.01 L, blood:gas at 1e4 and tissue:blood at 1e-3, with no fresh gas and
ventilation and cardiac output at their maximums. Compared with a 50-digit
reference (`_decimal_exponential` in `tests/unit/test_numerical_envelope.py`),
the worst propagator entry was off by 1.59e-11 at 0.1 s (19 squarings),
5.58e-9 at 100 s (28 squarings) and 5.65e-7 at 1464.4 s (32 squarings). A
60-column window from 0.99 drew 0.9900330968959383, and 59 times 5.65e-7 is
the 3.3e-5 excess. `docs/MODEL.md` § "The numerical envelope" records this.
No shipped agent needs more than 19 squarings over 24 hours, so shipped runs
are not affected. The input ceiling of 0.99 keeps the worst case inside the
ambient pressure. The error still applies to every drawn value at that
corner, not only near 1.

**Options.** Cap the display path's propagator interval, so that a long
column spacing chains shorter propagators with fewer squarings. Or compute the
exponential by a method that chooses fewer squarings for the same accuracy
(Al-Mohy AH, Higham NJ. A new scaling and squaring algorithm for the matrix
exponential. SIAM J Matrix Anal Appl 2009;31(3):970-989). Neither is needed
for a shipped agent today.
