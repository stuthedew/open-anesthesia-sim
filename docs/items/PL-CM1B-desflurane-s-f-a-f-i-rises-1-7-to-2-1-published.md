---
id: PL-CM1B
title: Desflurane's F_A/F_I rises 1.7 to 2.1 published SD faster than its Anesthesiology 1991 cohort from 1 to 10 minutes with F_I held at the airway, while the same volunteers' isoflurane and the sevoflurane cohort follow their curves, so something only desflurane has is too low
status: untriaged
touches: docs/MODEL.md, tests/reference/test_published_wash_in_and_elimination.py
added: 2026-10-18
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
