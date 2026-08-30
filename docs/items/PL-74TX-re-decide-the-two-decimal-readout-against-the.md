---
id: PL-74TX
title: Re-decide the two-decimal readout against the widened splitting-error measurement
status: untriaged
added: 2026-08-30
---

**Problem.** PL-040 chose a 0.01 percentage-point readout on the strength of
a measured solver error of 1.2e-2 percentage points at the worst reachable
*operating point* — about one count of the last displayed digit. PL-SLHS
re-measured that error over the reachable *trajectories* and it is 2.3e-2
percentage points, about two counts, and for a difference between two of the
six readouts it reaches 3.0e-2, about three counts. `docs/MODEL.md`
§ "Displayed precision" now states this accurately, but it states a weaker
version of the relationship than the one the decision was made on.

**Why it matters.** The decision itself may well survive: in ordinary use the
error is still a fifth of a count, and the alternative — a one-decimal
readout — would round the slow compartments to `0.0%` for minutes at a time,
which is the specific failure PL-040 rejected. What has changed is that the
justification no longer holds at the extreme, and the section now has to
carry a range spanning a factor of twelve rather than a single claim about
the last digit.

The compartment-*difference* finding is the newer half and is not addressed
by any resolution choice. The split's error is a systematic sequencing bias
whose sign is opposite at the two ends of the transfer chain, so the six
readouts placed in one row to be compared carry an error in their difference
larger than in either reading. Nothing in the interface says so.

**Where.** `docs/MODEL.md` § "Displayed precision"; `PL-040`'s recorded
decision; `src/anesthesia_sim/app/` wherever the readout resolution is
applied.

**Done when.** Either the two-decimal readout is reaffirmed against the new
measurement with the reasoning recorded, or the resolution changes and
`docs/MODEL.md` is revised with it; and the interface either conveys that a
gradient between two compartments is less certain than either reading, or
`docs/MODEL.md` records why it need not.
