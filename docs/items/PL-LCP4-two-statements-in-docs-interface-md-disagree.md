---
id: PL-LCP4
title: Two statements in docs/INTERFACE.md disagree with the tree: the open-circuit tail is not a third to a half of the mean curve over all of hours 8 to 13, and the use disclaimer is not beside the readouts
status: untriaged
feature: model-spec-accuracy
added: 2026-11-21
---

**Problem.** Two statements in docs/INTERFACE.md disagree with the tree: the open-circuit tail is not a third to a half of the mean curve over all of hours 8 to 13, and the use disclaimer is not beside the readouts

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. `docs/INTERFACE.md` belongs to the thread that is checking the interface specification against the code, so neither was corrected here.

1. § "Supported run length" (near "third to a half of the mean curve between hours 8 and 13"): with the rebreathing circuit removed, the model's tail over the published mean curve runs from 0.34 to 0.66 across hours 8 to 13, and three of the four cohorts are above a half at hour 8. "A third to a half" (0.34 to 0.46) is each cohort's lowest point, which comes near hour 8 for desflurane and near hour 13 for the others. `RECORDED_COMPARISONS` in `tests/reference/test_late_washout_against_published_fits.py` holds the figures. `docs/MODEL.md` now reads "falls to a third to a half of the mean curve at its lowest, near hour 8 for desflurane and near hour 13 for the others".
2. The sentence "standing disclaimers beside the readouts, one on interpretation and one on use": the use disclaimer (`USE_DISCLAIMER_TEXT` in `app/dashboard_frame.py`) is drawn at the foot of the window, not beside the readouts.

**Done when.** Both sentences agree with the tree.
