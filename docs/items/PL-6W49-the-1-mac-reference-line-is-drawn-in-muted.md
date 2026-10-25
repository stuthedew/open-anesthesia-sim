---
id: PL-6W49
title: The 1 MAC reference line is drawn in MUTED (#59728A) and the fat trace in FAT_COLOR (#64748B), 1.05:1 apart and both dashed, so during a washout, when fat is nearly flat, only the dash rhythm tells the reference from a compartment
priority: P2
effort: S
status: ready
classes: ux
feature: replay-findings
touches: src/anesthesia_sim/app/theme.py, tools/contrast_check.py, docs/MODEL.md
added: 2026-10-25
payoff: during a washout a reader cannot take the flat fat trace for the 1 MAC anchor, or the anchor for a seventh compartment
verify: grep -qF 'told apart from the fat trace' tools/contrast_check.py
---

**Problem.** `ONE_MAC_LINE_COLOR = MUTED` (`src/anesthesia_sim/app/theme.py`) and `FAT_COLOR = "#64748B"` measure 1.05:1 against each other. Both lines are dashed, at [16, 8] and [12, 4, 2, 4]. After a long case the fat trace stays near-flat for tens of minutes, so it has the same "constant horizontal line" look that the comment on the two chart references in `theme.py` relies on to mark a reference. `tools/contrast_check.py` measures each colour only against PANEL.

**Why it matters.** `docs/MODEL.md` requires a reference to be visually distinct in kind from a compartment trace. A reader matching colour to the legend can take the fat trace for the 1 MAC anchor, or the reference for a seventh compartment. The square-cap dash fault in PL-88MK makes the dash rhythms harder to tell apart still. The legend half of the original finding is fixed: Qt swatches now carry each series' dash. This may count as safety-critical if the owner judges the confusion to be misleading.

**Done when.** The 1 MAC reference line and the fat trace are told apart by more than their dash rhythm, and `tools/contrast_check.py` declares a requirement between `ONE_MAC_LINE_COLOR` and `FAT_COLOR` whose description contains the words "told apart from the fat trace", so `make check` refuses a pair that falls back to 1.05:1.

**Found by.** `PL-TBQS` reviewer replay on #288, findings r03 F2 and r06 F1. Checked against main on 2026-10-25; ratio computed from the theme constants.

**Generator check.** Shares one fact with `PL-GT8W`: `tools/contrast_check.py` measures each chart series only against `PANEL`, never against another series or a composite background the chart draws. Two items are not a generator, and a third would make one.
