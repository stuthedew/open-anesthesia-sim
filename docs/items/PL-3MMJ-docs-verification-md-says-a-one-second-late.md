---
id: PL-3MMJ
title: docs/VERIFICATION.md says a one-second-late control change moves a reading less than one standard deviation of any partition coefficient, and that blood:gas gives the smallest shift; its own uncertainty table shows the vessel-rich and fat shifts are smaller than both
priority: P1
effort: S
status: ready
classes: defect, science
feature: model-spec-accuracy
touches: docs/VERIFICATION.md
added: 2026-11-22
payoff: a developer reading the verification document learns correctly which coefficient uncertainties the one-second timing error is smaller than
---

**Problem.** docs/VERIFICATION.md says a one-second-late control change moves a reading less than one standard deviation of any partition coefficient, and that blood:gas gives the smallest shift; its own uncertainty table shows the vessel-rich and fat shifts are smaller than both

**Where.** `docs/VERIFICATION.md` § "Numerical method" says of the
one-second step, in its list of what the method supports: "For an ordinary dial change, that delay moves a displayed
value by less than one standard deviation of any measured partition
coefficient does." § "Supported simulation step", in the paragraph before
"**What one second does not buy.**", says "The blood:gas shift is the smallest of the four coefficients' shifts"
and concludes that "the timing error of an ordinary control action is smaller
than the shift from one SD of any coefficient".

**What the numbers say.** The same section's table gives the timing error as
up to 0.073 percentage points, for desflurane at case opening. `docs/INTERFACE.md`
§ "Why the readouts show two decimals" and `docs/MODEL.md` § "Precision"
give the largest first-hour shift from one SD of each coefficient: blood:gas
0.090, vessel-rich 0.054, muscle 0.99, fat 0.040, all for desflurane, and
`tests/integration/test_parameter_uncertainty.py` holds those ranges. So the
vessel-rich and fat shifts are smaller than the blood:gas shift and smaller
than the timing error. These are the figures after `PL-LBVN` stored
Mapleson's MAC at age 40 (pull request #2223); before it the timing error was
0.066 and the shifts 0.082, 0.049, 0.90 and 0.036, and the comparison came out
the same way. `PL-GHT6` found the same claim from the `PL-LBVN` branch and was
dropped as a duplicate of this item.

**Fix.** State the comparison as the numbers give it: the delay matters less
than the uncertainty in the blood:gas and muscle coefficients, and more than
that in the vessel-rich and fat coefficients. `PL-48MX` made the same
correction in `docs/MODEL.md` § "When a control change takes effect". Then
check whether the step's adequacy argument still holds as worded.

**Found by** the second blind review of `PL-48MX` (pass 1, finding 1),
2026-11-22, and checked against the table.

**Why it matters.** `docs/VERIFICATION.md` is where a developer learns whether the one-second step is good enough. A false comparison there could let a later change argue that the step's timing error is negligible against every coefficient, when for two of the four it is not.

**Done when.** Both sentences in `docs/VERIFICATION.md` state the comparison as the table's numbers give it, as `docs/MODEL.md` § "When a control change takes effect" already does, and the step's adequacy argument still holds as worded or is corrected.

**Generator check.** A one-off: the second copy of a claim whose first copy `PL-48MX` corrected; that item's review found this one.

**Reproduced 2026-11-23.** `docs/VERIFICATION.md` on `main` at `d219e317` still says "less than one standard deviation of any" and "The blood:gas shift is the smallest".
