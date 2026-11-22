---
id: PL-GHT6
title: docs/VERIFICATION.md § Supported simulation step says the case opening's one-second timing error is smaller than one SD of any partition coefficient, but its 7.3e-2 pp exceeds the vessel-rich (5.4e-2 pp) and fat (4.0e-2 pp) first-hour shifts that INTERFACE.md tabulates
status: dropped
feature: model-claims-held-by-tests
touches: docs/VERIFICATION.md
added: 2026-11-22
closed: 2026-11-22
reason: duplicate of PL-3MMJ (docs/VERIFICATION.md says a one-second-late control change moves a reading less than one SD of any partition coefficient), the same finding from the PL-48MX review; PL-3MMJ merged first in #2222, and its brief now carries this item's figures from after PL-LBVN, so nothing is lost
---

**Problem.** `docs/VERIFICATION.md` claims that a one-second delay in an
ordinary control change moves a displayed value by less than one standard
deviation (SD) of any measured partition coefficient. Its own figures and the
table it points to say otherwise for two of the four coefficients.

The claim, quoted from `docs/VERIFICATION.md` on branch
`work/pl-lbvn-replay` (2026-11-22), in two places:

1. The summary list under "The model takes one length of step": "For an
   ordinary dial change, that delay moves a displayed value by less than one
   standard deviation of any measured partition coefficient does."
2. § "Supported simulation step": "In the first hour at 1 MAC, one standard
   deviation (SD) of the blood:gas coefficient displaces a displayed
   compartment by up to $`9.0\times10^{-2}`$ pp, and one SD of the muscle
   coefficient by up to $`9.9\times10^{-1}`$ pp. The blood:gas shift is the
   smallest of the four coefficients' shifts, and the muscle shift is the
   largest. So the timing error of an ordinary control action is smaller than
   the shift from one SD of any coefficient, and in that sense the step is
   fine enough."

The same section's table gives the case opening (dial off to 1 MAC, reference
flows) a worst displacement of 7.3×10⁻² pp, for desflurane.

`docs/INTERFACE.md` § "Why the readouts show two decimals" tabulates the
largest first-hour shift from one SD of each coefficient. Its upper ends are
9.0×10⁻² pp for blood:gas, 5.4×10⁻² pp for vessel-rich tissue:gas,
9.9×10⁻¹ pp for muscle and 4.0×10⁻² pp for fat. So blood:gas is not the
smallest of the four, and 7.3×10⁻² pp is larger than the vessel-rich and fat
shifts. The claim was already wrong on the old MAC values: before `PL-LBVN`
the case opening was 6.6×10⁻² pp, against first-hour shifts of 4.9×10⁻² pp
for vessel-rich and 3.6×10⁻² pp for fat.

**Why it matters.** A developer reads this section to decide whether the
one-second step is fine enough. The sentence tells them the step's timing
error is below every coefficient's uncertainty, which the numbers do not
support.

**What a fix has to decide.** Either restate the comparison against the
coefficient whose shift is smallest, and say plainly that the case opening's
timing error is larger than one SD of the vessel-rich and fat coefficients
moves a readout, or compare like with like (for example, the shift in the same
compartment the timing error moves). Either way, a test should compute the
comparison, so the sentence cannot drift again when a stored value changes.

Found while replaying `PL-LBVN` (the MAC at age 40) onto the verification
document's new home; not fixed there because a defect in
`docs/VERIFICATION.md` is filed rather than fixed in place.

**Duplicate of `PL-3MMJ`**, recorded 2026-11-22. `PL-3MMJ` (filed on pull
request #2222, the clinician's rewrite of `docs/MODEL.md`) is the same
finding. Whichever of #2222 and #2223 merges second drops its copy as a
duplicate of the other and keeps the more current figures. This branch's
figures, at Mapleson's MAC at age 40, are a case-opening timing error of
7.3e-2 percentage points against one-SD shifts of 9.0e-2 (blood:gas), 9.9e-1
(muscle), 5.4e-2 (vessel-rich) and 4.0e-2 (fat).
