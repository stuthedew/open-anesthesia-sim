---
id: PL-7PLY
title: formatting.py's displayed-precision comment stops at the 1.2e-2 envelope corner and omits the 2.3e-2 worst trajectory, the row that actually tests its 'second decimal is the uncertain digit' claim
priority: P1
effort: S
status: ready
classes: science, docs
feature: presentation-safety
touches: src/anesthesia_sim/app/formatting.py
added: 2026-09-05
verify: uv run pytest tests/unit/test_formatting.py && grep -q '2.3e-2' src/anesthesia_sim/app/formatting.py
---

**Problem.** The comment above `CONCENTRATION_DISPLAY_DECIMALS` in
`src/anesthesia_sim/app/formatting.py` justifies the two-decimal readout from
two rows of the splitting-error measurement and stops there:

> the split disagrees with the independent solution by up to 5e-3 percentage
> points at the default flows and 1.2e-2 at the extreme corner of the settings
> envelope, so the second decimal is the uncertain digit

Both figures are correct as stated. What is missing is the row the conclusion
actually rests on. `docs/MODEL.md` § "Displayed precision" tabulates six runs,
and the last of them — *the worst reachable trajectory* — is 2.3×10⁻²
percentage points, with 3.0×10⁻² for a difference between two of the six
readouts (`PL-74TX`, re-decide the two-decimal readout against the widened
splitting-error measurement). The comment carries rows three and four and not
row six.

**Why it matters.** At 1.2e-2 the last displayed digit is uncertain by about
one count, which is what "the second decimal is the uncertain digit"
ordinarily means. On the worst reachable trajectory it is uncertain by about
two counts, and by about three for a gradient read between two compartments —
`docs/MODEL.md` says exactly this, in the same section, three paragraphs
below the table.

The conclusion survives: `PL-74TX` re-affirmed two decimals against the
widened measurement, because a one-decimal readout prints `0.0%` for the fat
fraction for an entire hour. What the comment records is the weaker argument
rather than the one that was made, and it is the recorded provenance for a
safety-critical constant — the same block tells the next reader that "changing
this is a safety-critical change to how a clinical value reads ... revise the
documented basis with it". A maintainer who re-decides the readout from this
comment alone is working from a bound half the measured one, and would find
the margin above the solver error twice what it is.

This is the same defect, in the same words and from the same table, that
`PL-X9HM` (README's status section understates the solver disagreement as
1.2e-2 where MODEL.md gives 2.3e-2 for the same domain) found in `README.md`
and corrected on 2026-09-05 — that file has since been deleted by `PL-WB5K`,
but its classification is the precedent here: `science`, not a wording nit.

Nothing catches it. `tools/doc_check.py` resolves cited paths and marked prose
values in documentation; a figure inside a Python comment is neither, so the
tree can disagree with `docs/MODEL.md` about a measured bound while `make
check` stays green.

**Where.** `src/anesthesia_sim/app/formatting.py`, the comment block above
`CONCENTRATION_DISPLAY_DECIMALS` — the sentence beginning "The short version".
`docs/MODEL.md` § "Displayed precision" is already correct and is the source to
quote from; it needs no edit, which is what keeps this item off the
non-delegable list.

**Overlaps `PL-88GQ`** (state every displayed decimal count as a presentation
decision the owner can revise, P2, `ready`), which rewrites this same comment
block to say the two-decimal choice was a choice rather than a derivation. The
two corrections pull in the same direction and are compatible, but whichever
lands second must fold the other in rather than replacing the block wholesale.

**Found.** Triage pass, 2026-09-06, reading `PL-X9HM`'s fix for the same
figure in the file that no longer exists.

**Done when.** The comment gives the trajectory-wide 2.3e-2 bound alongside
the 5e-3 and 1.2e-2 operating-point figures, and its claim about the last
displayed digit is true of the widest of them rather than only the narrowest.
