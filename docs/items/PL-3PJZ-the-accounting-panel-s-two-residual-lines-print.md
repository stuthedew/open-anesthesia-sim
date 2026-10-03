---
id: PL-3PJZ
title: The accounting panel's two residual lines print four significant digits of floating-point noise: the last-bit change PL-2MD9 made to the propagator moved them on 1,885 of 2,511 branch samples between v0.5.21 and v0.5.22, by up to 3.6 times, so only the order of magnitude the lines exist for carries information
status: untriaged
added: 2026-10-03
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
