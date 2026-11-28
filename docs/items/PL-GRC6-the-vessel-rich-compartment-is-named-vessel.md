---
id: PL-GRC6
title: The vessel-rich compartment is named 'Vessel-rich' in the chart's legend, its hover and the mark editor, and 'Vessel-rich group' in its readout, because READOUT_PANELS in app/dashboard_frame.py holds a second copy of each compartment's name and gloss
status: untriaged
feature: one-source-of-truth
added: 2026-11-27
---

**Problem.** The vessel-rich compartment is named 'Vessel-rich' in the chart's legend, its hover and the mark editor, and 'Vessel-rich group' in its readout, because READOUT_PANELS in app/dashboard_frame.py holds a second copy of each compartment's name and gloss

**Where.** `run_series.COMPARTMENT_NAMES` is the one record of each compartment's on-screen name since `PL-5867`, and `chart_frame.COMPARTMENT_TRACES` reads its labels from it. `dashboard_frame.READOUT_PANELS` still writes each name out again, with each gloss ("inspired", "end-tidal-equivalent"), which `COMPARTMENT_TRACES` also holds. The two copies agree except for one compartment: the readout says "Vessel-rich group" and the legend, the hover, the mark editor and a refused mark's notice say "Vessel-rich".

**Source.** NUREG-0700 Rev. 3 (O'Hara, Brookhaven National Laboratory for the U.S. Nuclear Regulatory Commission, July 2020; full text from https://www.osti.gov/servlets/purl/1644018, read 2026-11-27), guideline 1.3.3-4, p. 1-39: "Labels should be worded consistently, so that the same item is given the same label whenever it appears."

**What to decide.** Which of the two names the compartment carries everywhere. The choice is wording, so it is decided from a source, and the item records which.

**Done when.** `READOUT_PANELS` reads each name and gloss from the one record, every place names the vessel-rich compartment the same way, and the approved interface strings record any changed label.

**Found by** `PL-5867` on 2026-11-27, while finding the one place that names a compartment.
