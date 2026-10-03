---
id: PL-K1VH
title: Add a reader-chosen fixed ceiling to the compartment chart's shared MAC axis from a short ladder (1.5, 3 default, 4.5 MAC), labelled in both units, displayed in words beside the plot as the time base is, holding across runs and across a comparison, with no continuous auto-scale; record the ladder and the refusal beside docs/MODEL.md's 'Why the axis is fixed rather than fitted' (PL-V67Q's design round, project owner 2026-10-03, ratified)
priority: P2
effort: M
status: ready
classes: feature, ux
feature: chart-readout
touches: src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/dashboard_frame.py, docs/MODEL.md, tests/unit/test_chart_frame.py, tests/unit/test_dashboard_frame.py, tests/unit/test_formatting.py
added: 2026-10-03
payoff: a reader fits the chart to a low- or high-MAC lesson by choosing a fixed ceiling, and the axis never rescales on its own
verify: grep -qiF 'auto-scale' docs/MODEL.md && grep -q 'def test_axis_ceiling_ladder' tests/unit/test_chart_frame.py
---

**Problem.** Add a reader-chosen fixed ceiling to the compartment chart's shared MAC axis from a short ladder (1.5, 3 default, 4.5 MAC), labelled in both units, displayed in words beside the plot as the time base is, holding across runs and across a comparison, with no continuous auto-scale; record the ladder and the refusal beside docs/MODEL.md's 'Why the axis is fixed rather than fitted' (PL-V67Q's design round, project owner 2026-10-03, ratified)

**From `PL-V67Q`'s design round, 2026-10-03** (project owner, ratified). The chart today fixes one axis at 0-3 MAC (`CHART_AXIS_TOP_MAC`, `app/formatting.py`), labelled in percent on the left and MAC on the right, on `PL-CC23`'s reasoning that an axis which grows mid-lesson redraws the same physiology at a different height. This item adds a reader-chosen *fixed* ceiling from a short ladder - 1.5 MAC (1 MAC at two thirds of the height), 3 MAC (the default, desflurane's dial maximum), 4.5 MAC (above every shipped agent's dial maximum, so nothing is off scale) - with the exact rungs measured against `MAC_AXIS_STEP_LADDER_MAC`'s ruling and the MAC-awake band at each. The chosen range is stated in words beside the plot as the time base is (`docs/MODEL.md` § on the time base being a displayed mode), holds across runs and across both runs of a comparison, and resets with the application until the chart's modes get persistence. **Continuous auto-scale is refused**, not merely off: the truncation bias survives explicit markers (Correll, Bertini, Franconeri, CHI 2020, https://doi.org/10.1145/3313831.3376222; Witt, Meta-Psychology 2019, https://doi.org/10.15626/MP.2018.895; Huber and Huber, Exp Econ 2018, https://doi.org/10.1007/s10683-018-09598-4), and `PL-V67Q`'s design-round section carries the reading. Optional, if wanted in the same build: a one-shot *fit to run* that picks the lowest rung above the drawn maximum and then stays fixed. `docs/MODEL.md` records the ladder, the mode display and the refusal beside § "Why the axis is fixed rather than fitted". The control's home follows the time-base selector's; this is a chart control, not an Area behaviour. `PL-DVDY` (the off-scale notice in both units) belongs with it.

**Why it matters.** One fixed 0-3 MAC axis serves a lesson held near 1 MAC
poorly, with 1 MAC a third of the way up the plot, and cuts off the trace of
any agent whose dial maximum lies above 3 MAC. A reader-chosen fixed ceiling
serves both without the axis ever redrawing itself mid-lesson, which is what
`PL-CC23` refused an auto-scale for.

**Done when.** A reader chooses the chart's ceiling from the ladder the design
round named - 1.5, 3 by default, and 4.5 MAC, the rungs confirmed against
`MAC_AXIS_STEP_LADDER_MAC` and the MAC-awake band at each - the axis is
labelled in percent and MAC at every rung, the chosen range is stated in words
beside the plot, it holds across runs and across both runs of a comparison,
nothing rescales on its own, and `docs/MODEL.md` records the ladder, the mode
display and the refusal of continuous auto-scale beside § "Why the axis is
fixed rather than fitted".
