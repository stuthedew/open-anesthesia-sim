---
id: PL-CM1B
title: Desflurane's F_A/F_I rises 1.7 to 2.1 published SD faster than its Anesthesiology 1991 cohort from 1 to 10 minutes with F_I held at the airway, while the same volunteers' isoflurane and the sevoflurane cohort follow their curves, so something only desflurane has is too low
priority: P1
effort: M
status: done
classes: science
feature: validation-resolving-power
touches: docs/MODEL.md
added: 2026-10-18
closed: 2026-10-18
pr: 1531
payoff: a reader of docs/MODEL.md learns whether desflurane's fast early wash-in comes from one stored coefficient or is a limitation of the Gas Man set, measured rather than guessed
verify: grep -qF 'No single stored coefficient, moved within what was measured' docs/MODEL.md
---

**Problem.** Desflurane's F_A/F_I rises 1.7 to 2.1 published SD faster than its Anesthesiology 1991 cohort from 1 to 10 minutes with F_I held at the airway, while the same volunteers' isoflurane and the sevoflurane cohort follow their curves, so something only desflurane has is too low

**Evidence.** `PL-R0NL` compared the model's early wash-in with Figure 2 of
Yasuda et al., *Anesthesiology* 1991;74:489-98, page 493, read from the page
scan (`docs/references/yasuda-1991-figure-2-wash-in.md`). The run held F_I at
the airway, as the paper's non-rebreathing circuit did. Measured 2026-10-18:

| Minutes | Model | Published mean ± SD | Distance |
| --- | --- | --- | --- |
| 1 | 0.614 | 0.580 ± 0.019 (SD from the 3-minute bar) | +1.79 SD |
| 3 | 0.766 | 0.731 ± 0.019 | +1.82 SD |
| 5 | 0.827 | 0.792 ± 0.019 | +1.82 SD |
| 7.5 | 0.864 | 0.832 ± 0.019 | +1.70 SD |
| 10 | 0.882 | 0.840 ± 0.020 | +2.10 SD |
| 12.5 | 0.891 | 0.872 ± 0.020 | +0.94 SD |
| 25 | 0.906 | 0.900 ± 0.020 | +0.28 SD |

The same eight volunteers breathed isoflurane from the same cylinder, and the
model's isoflurane follows that cohort's curve within one SD at every point
but 12.5 minutes (+1.06 SD). Sevoflurane and isoflurane in the *Anesth Analg*
cohort both sit slightly below their curves in the first 3 minutes (-0.54 to
-0.83 SD). An error in ventilation or lung volume would move every agent the
same way, so the cause is likely something only desflurane has: its
blood:gas coefficient (0.42 stored), or its vessel-rich or muscle tissue:gas
coefficient. The reading error of the figure is about 0.006 in a mean, which
is 0.3 SD here, so it does not explain a gap of 0.034 to 0.042.

**What holds it now.** `EARLY_WASH_IN_DISAGREEMENTS` in
`tests/reference/test_published_wash_in_and_elimination.py` holds those five
desflurane points to a regression band, from -1 SD to +2.5 SD, so the gap
cannot grow unseen.

**Why it matters.** Wash-in is the curve the simulator most displays, and a
learner reads desflurane's speed off it. A model that rises 0.034 to 0.042
faster in F_A/F_I over the first 10 minutes than the human cohort it is
compared with overstates how fast desflurane reaches the brain, and so how
fast induction and a dial change take effect. If one stored coefficient
explains it, that coefficient is wrong for this model; if none does, the
disagreement is a limitation a reader should be told about.

**Done when.** The measurement is recorded in `docs/MODEL.md` § "The early
wash-in curve against the published figures": which desflurane coefficient, if
any, moved within its published measurements, brings the 1-to-10-minute
points within one SD without moving the 30-minute comparison or the
elimination out of their bands, and what that leaves. No stored value changes
here; a change is the owner's decision.

**Generator check.** One-off: a validation finding from the first comparison
of the early curve with published data (`PL-R0NL`), not a misread fact.

**Related.** `PL-RFLN` (done) settled desflurane's five-minute washout residual
as end-tidal sampling or the published datum. A desflurane that is too
insoluble would wash in too fast and wash out too fast, so the two findings
may share a cause, and the investigation should test that.

**Recommended work.** Measure which single desflurane coefficient, moved
within its published measurements, brings the 1-to-10-minute points inside one
SD without moving the 30-minute ratio or the elimination out of their bands.
Compare the stored blood:gas coefficient with the primary measurements cited
in `src/anesthesia_sim/data/agents/desflurane.json`. Record the answer; change
a stored value only on the owner's decision, since it is a clinical value.

**Closed 2026-10-18 on the recorded answer: no single coefficient closes the
gap.** Each desflurane coefficient was moved alone through the reference
test's own harness (`StoredParameterChange`, `_clamped_wash_in`,
`_wash_in_ratio` and `_eliminate`), and the baseline reproduced this item's
table to four places. Blood:gas brings the 1-to-10-minute points within one
SD from about 0.55, and Esper et al. 2015's 0.57 ± 0.04 puts them all within
0.83 SD. But the 30-minute ratio holds its one-SD band at every fresh gas flow
from 1 to 10 L/min only up to about 0.46, and at 0.57 fails at every flow,
from −1.35 SD at 10 L/min to −2.61 SD at 1 L/min. The vessel-rich and muscle
coefficients cannot close the gap within Yasuda et al. 1989's measurements.
Taking Esper's values for all three agents puts sevoflurane's and
isoflurane's first-3-minute points 1.0 to 1.4 SD below their curves. Raising
blood:gas to 0.57 moves the `PL-RFLN` washout residual only from −2.33 to
−1.97 SD. `docs/MODEL.md` § "The early wash-in curve against the published
figures" records all of this and keeps the disagreement as a known
limitation, still held by the regression band. Nothing stored changes, and no
owner decision is asked: keeping the Gas Man set is the owner's decision of
2026-09-03 (`PL-D6LX`), and `ROADMAP.md`'s planned-milestone item 31 is where a
primary set, and this gap with it, would be weighed.
