---
id: PL-S0HP
title: With PL-571L's half-line top margin, re-measure whether a hover box with every trace fits a concentration plot at its least height, under the container's font and CI's
status: untriaged
feature: chart-readout
added: 2026-11-22
---

**Problem.** With PL-571L's half-line top margin, re-measure whether a hover box with every trace fits a concentration plot at its least height, under the container's font and CI's

**Found on 2026-11-22** by the blind review of #2225, as an optional finding. PL-571L gives the plot a top margin of half a font line, so the top tick label is drawn whole. That margin comes out of the data area, and the plot's least height (`theme.CHART_LEAST_HEIGHT`, 160 px) did not grow with it.

**What was measured.** Offscreen, in the container's font, the concentration plot's data area at its least height is 113 px with the margin. PL-YJ7N measured it at about 120 px before, and measured a box reporting several traces at up to 113 px. The tallest box over the Induction dashboard's 222 test points was 53 px. So the tallest box PL-YJ7N measured now just fits, and a taller one, or CI's font (DejaVu Sans), could leave the box's bottom line clipped by the plot. That line is a value the learner is reading.

**Done when.** The tallest box the concentration plot can show (every trace of two compared runs) is measured against the data area at the least height, under both fonts. Where it does not fit, the least height grows by the margin, and the 1366 by 768 layouts are checked again.
