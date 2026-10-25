---
id: PL-GT8W
title: The MAC-awake band's 14% INK fill drops the alveolar trace from 3.61:1 to 2.82:1 and the muscle trace from 3.43:1 to 2.68:1 inside the band, below SC 1.4.11's 3:1, exactly where a learner compares crossings, and tools/contrast_check.py measures traces only against PANEL so make check cannot see it
priority: P2
effort: M
status: ready
classes: ux
feature: replay-findings
touches: src/anesthesia_sim/app/theme.py, tools/contrast_check.py, docs/MODEL.md
added: 2026-10-25
payoff: the traces stay legible exactly where a learner compares crossings, and the contrast check can see a fill that breaks that
verify: grep -qF 'the MAC-awake band composite' tools/contrast_check.py
---

**Problem.** `MAC_AWAKE_BAND_FILL_OPACITY = 0.14` (`src/anesthesia_sim/app/theme.py`) tints the band INK over a white panel. The composite is about #E0E4E7. Against it, on main's colours, alveolar measures 2.82:1 and muscle 2.68:1, against 3.61 and 3.43 on PANEL. The comment above it says the fill is light enough for six traces to stay legible across it. The `Requirement` table in `tools/contrast_check.py` measures every trace only on PANEL and the band only by its edge.

**Why it matters.** The band is where the alveolar and vessel-rich crossings are compared, so it is where trace legibility matters most. The check reports no shortfall while the fill creates two. A fix could lighten the fill, or add the band composite as a background that every trace is measured against.

**Done when.** Every compartment trace reaches 3:1 against the MAC-awake band's composite colour, and `tools/contrast_check.py` measures each trace against that composite as a background named "the MAC-awake band composite", so `make check` refuses a fill that drops a trace below 3:1.

**Found by.** `PL-TBQS` reviewer replay on #288, finding r05 F2. Checked against main on 2026-10-25 with the WCAG relative-luminance formula on the theme constants. Run `tools/contrast_check.py` to confirm once the composite is declared.

**Generator check.** Shares one fact with `PL-6W49`: `tools/contrast_check.py` measures each chart series only against `PANEL`, never against another series or a composite background the chart draws. Two items are not a generator, and a third would make one.
