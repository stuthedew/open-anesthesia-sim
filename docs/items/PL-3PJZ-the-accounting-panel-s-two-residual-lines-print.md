---
id: PL-3PJZ
title: The accounting panel's two residual lines print four significant digits of floating-point noise: the last-bit change PL-2MD9 made to the propagator moved them on 1,885 of 2,511 branch samples between v0.5.21 and v0.5.22, by up to 3.6 times, so only the order of magnitude the lines exist for carries information
priority: P3
effort: S
status: done
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_formatting.py, tests/unit/test_dashboard_frame.py, docs/MODEL.md
added: 2026-10-03
closed: 2026-10-03
pr: 1301
verify: uv run pytest tests/unit/test_formatting.py && grep -q 'def test_format_agent_residual_prints_no_digit_a_last_bit_change_redraws' tests/unit/test_formatting.py
---

**Problem.** The accounting panel's two residual lines print four significant digits of floating-point noise: the last-bit change PL-2MD9 made to the propagator moved them on 1,885 of 2,511 branch samples between v0.5.21 and v0.5.22, by up to 3.6 times, so only the order of magnitude the lines exist for carries information

**What the lines print, and what they are for.** `format_agent_residual` in
`src/anesthesia_sim/app/formatting.py` renders the unaccounted amount and the
absolute error as `f"{litres:.3e} L"`, four significant digits, and the comment
on `AGENT_RESIDUAL_DISPLAY_DECIMALS` says exponent form was chosen because an
order of magnitude is what those two lines are for: a fixed one-decimal line
would read `0.0 L` and say nothing (`PL-TG60`).

**Measured 2026-10-03, while cutting v0.5.22** (`PL-KXW1`). `PL-2MD9` changed
the propagator at the last bits, so the cut played 81 runs on the v0.5.21 tag
and on its own tree and forked each at minute 30. On the branches, which open
from the moved canonical keyframe, the two lines read differently on 1,885 of
2,511 per-minute samples (`5.601e-14 L` against `5.609e-14 L`), by up to 3.6
times between the two trees, and 32 of the 3,770 differing strings changed
exponent. No value either side exceeded 5.4e-11 L, so the conservation check
passed by the same margin in both; what moved is only the digits the line
asserts. The trunk's lines were identical, because its stepped path is.

**Why it may matter.** `CLAUDE.md`'s safety-critical standard asks that
formatting precision be justified by model fidelity and practical
interpretability. Four significant digits on a residual whose mantissa is
rounding noise assert a resolution the value does not have, and a reader
comparing a trunk with its branch sees two different numbers for the same check
passing. One significant digit, or the order of magnitude alone, would carry
everything the line is for; which form is a display decision for triage, not
settled here.

**Closed 2026-10-03: each line prints the power of ten it lies below**
(project owner, 2026-10-03, ratified, over one significant digit, over the
nearest decade and over keeping the sign).
`format_agent_residual` now renders `<1e-13 L` - the smallest power of ten the
residual's magnitude lies strictly below, from `Decimal(abs(x)).adjusted() + 1`
so the decade is exact for the float's own value - and `0 L` for exactly zero.
`AGENT_RESIDUAL_DISPLAY_DECIMALS` is gone, having no count left to hold.
`docs/MODEL.md` § "Displayed precision" carries the reasoning and the figures.

**The form was chosen by measurement, not argument.** The cut's script was not
kept, so the protocol it records was replayed on the v0.5.21 tag and on
v0.5.22 (81 runs: sevoflurane dials 2/1, 3/1.5, 6/2 %; isoflurane 1.2/0.6,
2/1, 4/1.5; desflurane 6/3, 9/6, 18/6; cardiac output 4, 5, 6 L/min; fresh gas
0.5, 2, 5 L/min; dial changed at minute 30, closed at 50, fresh gas to 10 L/min
at 60, cardiac output +1 at 70, played to 91; each forked at 1800 s with the
first dial set back and the branch played 30 minutes; both residuals sampled
every minute and compared as `float.hex()`). The dial pairs are this replay's
own choice, which is why its 1,975 differing samples are not the cut's 1,885.
Of 2,511 branch samples, the candidate forms read differently on:

| Form | Samples differing |
| --- | --- |
| four significant digits (`.3e`, shipped) | 1,975 |
| two (`.1e`) | 634 |
| one (`.0e`) | 154 |
| decade bound, `<1e-13` (taken) | 22 |
| nearest decade, `~1e-13` | 16 |

Trunk samples: 0 of 7,452 differ in every form. Worst ratio between the two
trees' residuals for one branch sample: 5.9; residual sign flipped on 3;
largest residual 2.13e-11 L on both; no check failed (core runs
`require_valid_agent_accounting` every step, and neither replay halted).

**One significant digit was the item's other named option and was refused on
that table**: the leading digit of a value that a correct change moves by up to
5.9 times is still noise, and it read differently on 6% of samples against
under 1% for either decade form. **The bound was taken over the nearest
decade**, which differs on six fewer samples: `<` is the panel's existing
idiom (`format_agent_volume` prints `<0.1 L`), and a bound is a true statement
about the value where `~1e-13` for 3.5e-14 is an approximation a reader has to
be told the rounding rule of. **The sign was dropped with the mantissa**: a
passing residual's sign is the direction its rounding fell, and a failing check
halts the run with the signed values at six figures in the failure notice
(`halt_disposition` in `app/dashboard_frame.py` records the exception's text).
Both lines therefore always read alike - captured as its own item rather than
decided here, since whether to fold them is a change to what the panel shows.

**Regression test**: `test_format_agent_residual_prints_no_digit_a_last_bit_change_redraws`
pins the pair `5.601e-14`/`5.609e-14` the cut recorded for one sample.
`test_format_agent_residual_bound_is_strict_and_tight_at_every_power_of_ten`
pins the exactness: `math.log10` places the float written `1e-16`, exactly
9.99...e-17, a decade too high.
