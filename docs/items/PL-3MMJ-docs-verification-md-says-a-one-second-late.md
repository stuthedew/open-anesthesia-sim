---
id: PL-3MMJ
title: docs/VERIFICATION.md says a one-second-late control change moves a reading less than one standard deviation of any partition coefficient, and that blood:gas gives the smallest shift; its own uncertainty table shows the vessel-rich and fat shifts are smaller than both
priority: P1
effort: S
status: done
classes: defect, science
feature: model-spec-accuracy
touches: docs/VERIFICATION.md
added: 2026-11-22
closed: 2026-11-23
pr: 2310
payoff: a developer reading the verification document learns correctly which coefficient uncertainties the one-second timing error is smaller than
verify: grep -qF 'and by more than one of the vessel-rich or fat' docs/VERIFICATION.md
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

**Done 2026-11-23.** Both sentences now state the comparison the way the
uncertainty table in `docs/INTERFACE.md` § "Why the readouts show two
decimals" gives it. The one-second timing error of an ordinary control
action, up to 7.3×10⁻² pp (the case-opening row of the timing table in
`docs/VERIFICATION.md`), is smaller than the first-hour shift from one SD of
the blood:gas coefficient (up to 9.0×10⁻² pp) or the muscle coefficient (up to
9.9×10⁻¹ pp). It is larger than the shift from one SD of the vessel-rich
coefficient (up to 5.4×10⁻² pp) or the fat coefficient (up to 4.0×10⁻² pp),
which are the two smallest, not blood:gas. The summary bullet in § "What the
model was checked against" says the same. The conclusion that the step is
fine enough stands, on the narrower ground that the timing error is of the
same order as the smallest parameter uncertainty and more than ten times
smaller than the largest. Each figure was read from the two tables on
2026-11-23.

The blind review found the same wrong claim in the comment above
`SIMULATION_STEP_S` in `src/anesthesia_sim/core/simulation_step.py`, which
also named the source section by an old title. The comment now gives all four
shifts and the same comparison. It also found that the summary bullet had
dropped "in the first hour": over 24 h, one SD of the fat coefficient moves a
readout by up to 4.4×10⁻¹ pp, which is more than the timing error. The bullet
now carries the scope.

Docs checked: `docs/VERIFICATION.md`, both passages; the comment above
`SIMULATION_STEP_S`; `docs/INTERFACE.md`
§ "Why the readouts show two decimals", whose table is the source and needs no
change; `docs/MODEL.md` § "When a control change takes effect" already
states the comparison this way, with the same four figures.
