---
id: PL-PJWT
title: While the user previews zero alveolar ventilation, the F_A/F_I plot's preview region is empty and nothing says why
status: untriaged
feature: interface-design-review
added: 2026-11-27
filed-pr: 2329
---

**Problem.** While the user holds the alveolar ventilation slider at zero, the preview of the F_A/F_I plot draws nothing past the run's reach. Rule 3 of `src/anesthesia_sim/app/wash_in.py` (`PL-49D5`) leaves every predicted state without a ratio, because a step at zero ventilation reached it. The compartment chart still draws its preview, so the two plots show the same future, but the F_A/F_I plot's preview region is blank and its caption speaks only of the run's own state. A user cannot tell a blank preview from a preview that failed to draw.

**Found by** the domain review pass of `PL-49D5`'s close-out on 2026-11-27 (`s2_preview_coarse.py`, second block), as an optional finding. `PL-49D5` draws the one-point stretch at the reach as a dot, which shows where the run stands, and leaves the empty region.

**What to decide.** Whether the preview region of the F_A/F_I plot should say, while a zero-ventilation setting is previewed, that the ratio is not a wash-in fraction at zero ventilation, and where that text goes. `docs/INTERFACE.md` § "A preview of an unapplied setting" names the four cues a preview carries.
