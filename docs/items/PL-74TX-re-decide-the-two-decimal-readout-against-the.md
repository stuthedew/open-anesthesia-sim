---
id: PL-74TX
title: Re-decide the two-decimal readout against the widened splitting-error measurement
priority: P1
effort: S
status: done
classes: safety, docs
feature: numerical-domain
milestone: v0.2.7
touches: docs/MODEL.md, tests/reference/test_coupled_dynamics.py
added: 2026-08-30
closed: 2026-08-30
commit: f252aa4
pr: 69
verify: uv run pytest tests/reference/test_coupled_dynamics.py -k reverses_only_at_a_crossing
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

---

**Decided 2026-08-30: the readout stays at two decimal places.** Recorded in
`docs/MODEL.md` § "Displayed precision" as a re-affirmation against the
widened measurement rather than a restatement of PL-040, and the alternative
is what settles it: a one-decimal readout would be uncertain by a fifth of a
count even at the extreme, but at 0.1 percentage points the fat fraction
reads `0.0%` for an entire hour and muscle for its first three to fifteen
minutes — the failure that section already rejects. The widened measurement
moved where inside that window the answer sits, not which side of it. No code
changed; `CONCENTRATION_DISPLAY_DECIMALS` was already 2.

**The compartment-difference half is resolved by measurement, not by
marking.** The question was whether the interface must convey that a gradient
between two compartments is less certain than either reading. It need not,
and the reason is that the comparison the row invites is *ordinal* — the
circuit leads the alveoli lead the tissues — and an ordinal reading is
corrupted only if the error inverts which of two compartments is displayed as
higher.

Measured across every trajectory the gate drives, all three agents, every
pair of the six readouts at every step: no inversion at all at ordinary
settings, at the reference point, at the envelope corner, or across a
ventilator start. Inversions occur only on the worst reachable trajectory —
0.2 s of a 900 s run for sevoflurane, 1.7 s for desflurane — and only where
the two compartments are within 1.73 counts of the last displayed digit of
each other, which is to say only while they are crossing and the ordering is
genuinely ambiguous.

`test_displayed_ordering_reverses_only_at_a_crossing` holds that claim rather
than leaving it to the reply that made it: it fails if the split ever inverts
a displayed ordering between two compartments further apart than three
counts. That is 1.7x the measurement and far tighter than the arithmetic
alone would allow — two readings displaced in opposite directions by the full
error bound, plus rounding, could invert a gap of about 6.6 counts — so a
degradation that mattered would fail this well before it reached what the
bound permits.

The numeric *difference* between two readouts remains the least certain thing
on the display, and § "Displayed precision" says so plainly. What changed is
that the claim is now bounded where it matters instead of only disclosed.
