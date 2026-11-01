---
id: PL-81Q2
title: At the stiffest envelope corner the chart's 24-hour window advances each column by a 1464.4 s propagator that needs 32 squarings, the module's maximum, so each column carries an error of 5.65e-7 and 59 columns accumulate 3.3e-5; decide whether the display path should cap its propagator interval or use a method that avoids over-squaring (Al-Mohy and Higham 2009)
priority: P1
effort: S
status: done
classes: science
feature: floating-point-domain
touches: docs/MODEL.md
added: 2026-11-01
closed: 2026-11-01
pr: 1909
verify: grep -qF '(`PL-81Q2`, 2026-11-01)' docs/MODEL.md
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

**Why it matters.** The display path draws every value a learner reads off the
chart, so an error in it is a displayed-value error under `CLAUDE.md`'s
safety-critical standard, even at a corner no shipped agent reaches.

**Done when.** Each option is measured at the corner, the one taken (or
neither) is recorded in `docs/MODEL.md` § "The numerical envelope" with its
numbers, and the display path changes only if a remedy measurably shrinks the
error.

**Generator check.** One-off. The fact at issue is the error bound that
`core/matrix_exponential.py` § "What it costs" already states: it grows with
the interval times the fastest rate. No other open item reads that bound.

**Decided 2026-11-01: neither remedy, and the display path keeps its method.**
Both options were measured at the corner the brief names, over the window's
1464.4 s column spacing, against `_decimal_exponential`'s 50-digit reference.

- Capping the interval does not help. One propagator (32 squarings) was off by
  6.0e-7 in its worst entry. The same interval built from propagators over
  100 s, 10 s or 1 s (28, 25 or 22 squarings) was off by 5.9e-7, 5.8e-7 and
  5.8e-7. The shorter propagators carry smaller errors but are multiplied more
  times, as the module's bound predicts. The brief's per-propagator figures
  were right; the inference that fewer squarings per propagator would shrink
  the product was not.
- Al-Mohy and Higham's method saves squarings only where a matrix's norm far
  exceeds its spectral radius. Here the 1-norm is 1.83e5 /s and the spectral
  radius 1.67e5 /s, so a degree-13 Padé approximant still needs 26 squarings,
  and it would give up the shift that makes the propagator nonnegative in
  floating point.

No application run reaches the window: a stepped run at the stiffest corners
halts on the mass-balance check within a few dozen steps. The 3.3e-5 excess is
less than half of one displayed count (1e-4). The brief measured 5.65e-7 for
the single propagator; this measurement, with no fresh gas and the same
reference, gives 6.0e-7, and both are reported as measured.

This was the one clearly correct option once measured, so it was taken in the
thread rather than put as a decision (`.claude/rules/instruction-writing.md`
rule 14). The owner can reopen it on a measurement that a remedy helps.
