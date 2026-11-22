---
id: PL-3MMJ
title: docs/VERIFICATION.md says a one-second-late control change moves a reading less than one standard deviation of any partition coefficient, and that blood:gas gives the smallest shift; its own uncertainty table shows the vessel-rich and fat shifts are smaller than both
status: untriaged
feature: model-spec-accuracy
touches: docs/VERIFICATION.md
added: 2026-11-22
---

**Problem.** docs/VERIFICATION.md says a one-second-late control change moves a reading less than one standard deviation of any partition coefficient, and that blood:gas gives the smallest shift; its own uncertainty table shows the vessel-rich and fat shifts are smaller than both

**Where.** `docs/VERIFICATION.md` § "Numerical method" says of the
one-second step, in its list of what the method supports: "For an ordinary dial change, that delay moves a displayed
value by less than one standard deviation of any measured partition
coefficient does." § "Supported simulation step", in the paragraph before
"**What one second does not buy.**", says "The blood:gas shift is the smallest of the four coefficients' shifts"
and concludes that "the timing error of an ordinary control action is smaller
than the shift from one SD of any coefficient".

**What the numbers say.** The same paragraph gives the timing error as up to
0.066 percentage points, for desflurane at case opening. `docs/INTERFACE.md`
§ "Why the readouts show two decimals" and `docs/MODEL.md` § "Precision"
give the largest first-hour shift from one SD of each coefficient: blood:gas
0.082, vessel-rich 0.049, muscle 0.90, fat 0.036, all for desflurane, and
`tests/integration/test_parameter_uncertainty.py` holds those ranges. So the
vessel-rich and fat shifts are smaller than the blood:gas shift and smaller
than the timing error.

**Fix.** State the comparison as the numbers give it: the delay matters less
than the uncertainty in the blood:gas and muscle coefficients, and more than
that in the vessel-rich and fat coefficients. `PL-48MX` made the same
correction in `docs/MODEL.md` § "When a control change takes effect". Then
check whether the step's adequacy argument still holds as worded.

**Found by** the second blind review of `PL-48MX` (pass 1, finding 1),
2026-11-22, and checked against the table.
