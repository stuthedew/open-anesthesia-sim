---
id: PL-K1VH
title: Add a reader-chosen fixed ceiling to the compartment chart's shared MAC axis from a short ladder (1.5, 3 default, 4.5 MAC), labelled in both units, displayed in words beside the plot as the time base is, holding across runs and across a comparison, with no continuous auto-scale; record the ladder and the refusal beside docs/MODEL.md's 'Why the axis is fixed rather than fitted' (PL-V67Q's design round, project owner 2026-10-03, ratified)
priority: P2
effort: M
status: done
classes: feature, ux
feature: chart-readout
touches: src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/compartment_schematic.py, docs/INTERFACE.md, docs/VERIFICATION.md, docs/PARAMETERS.md, tests/unit/test_chart_frame.py, tests/unit/test_dashboard_frame.py, tests/unit/test_formatting.py, tests/unit/test_compartment_schematic.py, tests/integration/test_qt_chart.py, tests/integration/test_view_contract.py, tests/integration/test_dark_appearance.py, tests/integration/test_compartment_schematic_view.py, tests/integration/test_interface_wording.py, tests/integration/approved_interface_strings.json, tests/integration/simulation_view/test_simulation_view_halt.py
added: 2026-10-03
closed: 2026-11-22
pr: 2270
payoff: a reader fits the chart to a low- or high-MAC lesson by choosing a fixed ceiling, and the axis never rescales on its own
tests: tests/integration/test_view_contract.py::test_the_concentration_chart_saves_its_axis_top_and_is_built_again_at_it, tests/integration/test_view_contract.py::test_an_axis_top_picked_in_one_chart_redraws_only_that_chart, tests/integration/test_view_contract.py::test_a_chart_at_another_top_keeps_its_plot_when_handed_the_frame_it_already_shows, tests/unit/test_formatting.py::test_the_chart_ceiling_is_the_chosen_top_times_the_agent_s_mac, tests/unit/test_chart_frame.py::test_the_frame_draws_both_axes_at_the_top_it_carries
---

**Problem.** Add a reader-chosen fixed ceiling to the compartment chart's shared MAC axis from a short ladder (1.5, 3 default, 4.5 MAC), labelled in both units, displayed in words beside the plot as the time base is, holding across runs and across a comparison, with no continuous auto-scale; record the ladder and the refusal beside docs/MODEL.md's 'Why the axis is fixed rather than fitted' (PL-V67Q's design round, project owner 2026-10-03, ratified)

**From `PL-V67Q`'s design round, 2026-10-03** (project owner, 2026-10-03, ratified). The chart today fixes one axis at 0-3 MAC (`CHART_AXIS_TOP_MAC`, `app/formatting.py`), labelled in percent on the left and MAC on the right, on `PL-CC23`'s reasoning that an axis which grows mid-lesson redraws the same physiology at a different height. This item adds a reader-chosen *fixed* ceiling from a short ladder - 1.5 MAC (1 MAC at two thirds of the height), 3 MAC (the default, desflurane's dial maximum), 4.5 MAC (above every shipped agent's dial maximum, so nothing is off scale) - with the exact rungs measured against `MAC_AXIS_STEP_LADDER_MAC`'s ruling and the MAC-awake band at each. The chosen range is stated in words beside the plot as the time base is (`docs/MODEL.md` § on the time base being a displayed mode), holds across runs and across both runs of a comparison, and resets with the application until the chart's modes get persistence. **Continuous auto-scale is refused**, not merely off: the truncation bias survives explicit markers (Correll, Bertini, Franconeri, CHI 2020, https://doi.org/10.1145/3313831.3376222; Witt, Meta-Psychology 2019, https://doi.org/10.15626/MP.2018.895; Huber and Huber, Exp Econ 2018, https://doi.org/10.1007/s10683-018-09598-4), and `PL-V67Q`'s design-round section carries the reading. Optional, if wanted in the same build: a one-shot *fit to run* that picks the lowest rung above the drawn maximum and then stays fixed. `docs/MODEL.md` records the ladder, the mode display and the refusal beside § "Why the axis is fixed rather than fitted". The control's home follows the time-base selector's; this is a chart control, not an Area behaviour. `PL-DVDY` (the off-scale notice in both units) belongs with it.

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

**Checked 2026-11-22** against `d4e8200`: still applies. The chart still has one fixed ceiling, `CHART_AXIS_TOP_MAC` in `app/formatting.py`, and no control chooses another. The section the brief names, "Why the axis is fixed rather than fitted", does not exist. The reasoning it means is the paragraph "The chart's vertical range is set in MAC, and fixed" in `docs/INTERFACE.md` § "MAC multiples as a display unit", which is where the ladder and the refusal of auto-scale belong now.


**Done 2026-11-22** (with `PL-DVDY` and `PL-BNMZ`, one pull request). The chart's top is `ChartCeiling` in `app/formatting.py`: 1.5, 3 (standard, `CHART_AXIS_TOP_MAC`) and 4.5 MAC. Each concentration chart View holds its own top, chosen from an "Axis top" dropdown beside "Time base" (`ChartCeilingSelector` in `app/qt_chart.py`), and saves it as `ceiling_mac` beside its window in its version 2 state. A state with no key opens at 3 MAC with no notice; a value off the ladder opens at 3 MAC with the unreadable-state notice. The dashboard still assembles every frame at the standard top, so Views at one window share a frame; `ChartFrame` now carries `ceiling`, and `axis_top_percent`, `mac_ticks` and `percent_ticks` are properties that read it, so a View draws the shared frame at its own top with `dataclasses.replace`. `__post_init__` builds the top once, so a top past one atmosphere is still refused before any chart draws (`PL-7DJK`). The off-scale lines read the frame the View drew, so they report against the chosen top.

The rungs, checked against the MAC axis's step rule and the MAC-awake band: at 1.5 MAC the MAC axis is labelled every 0.25 (6 intervals), at 3 and 4.5 every 0.5 (6 and 9 intervals), within `MAX_MAC_AXIS_INTERVALS`. The MAC-awake band stays inside the plot at every rung, its top at 0.36 MAC for isoflurane. At 4.5 MAC no vaporizer can leave the plot (sevoflurane's 8% is 4.44 MAC). The optional one-shot "fit to run" was not built.

The compartment schematic keeps the standard 3 MAC scale whatever top a chart has, because the top is the chart View's own setting. Its caption no longer calls the scale the chart's, and its marks are the MAC axis's labels at the standard top rather than percent gridlines.

**Refusal of auto-scale**, recorded in `docs/INTERFACE.md` § "The chart's fixed MAC axis": Correll, Bertini and Franconeri, CHI 2020, doi:10.1145/3313831.3376222, abstract read 2026-11-22 from arXiv 1907.02035 ("the subjective impact of axis truncation is persistent across visualizations designs, even for designs with explicit visual cues"). The brief's Witt 2019 and Huber and Huber 2018 were not read in this session and are not cited in the document.

Docs checked: `docs/INTERFACE.md` (§ "The chart's fixed MAC axis", § "The chart's time base", § "Displayed precision", the schematic section and its note for developers, the MAC-awake band paragraph that names `CHART_AXIS_TOP_MAC`, which still holds at the standard top), `docs/VERIFICATION.md` (the fat-trace hazard row, which now names the reader-chosen top and says the 1.5 MAC top spreads every trace twice as tall, and the long-run shortfall paragraph), `docs/MODEL.md` (no mention of the ceiling), `README.md` (none).

**Where the control sits.** A placeholder, decided under rule 14: the "Axis top" control and the time base share a row of their own under the chart's heading. Beside the heading, the controls made the heading wrap at the Area's least width, and the View's least height at 1366 by 768 grew past what the Induction and Maintenance Workspaces have (page scrolled 5-33 px). Wrapping the two controls in a flow row stacked them and still grew the View by 32 px. The row of its own grows it by 18 px (278 to 296 px in the container's font, 276 to 294 px in DejaVu Sans), which both Workspaces hold without scrolling. The wash-in View keeps its time base beside its heading.

**Blind review.** Pass 1 and pass 2 both found that a chart at the 1.5 or 4.5 ×MAC top emptied its plot on a kept frame after the plot had widened, because the withhold check compared the kept frame with the chart's copy of it (should-fix, fixed in the next commit with a regression test that fails without the fix). Pass 1 found that "no setting leaves the plot" at 4.5 ×MAC holds only at the age-40 MAC, which age-adjusted MAC will lower (optional, fixed: the claim is stated at the age-40 MAC, and a new test reads each agent's stored MAC and vaporizer maximum). Pass 2 found that the schematic's and the off-scale test's docstrings still said the schematic shares the chart's axis (optional, fixed). Pass 2's finding also shows that with the chart at 1.5 or 4.5 ×MAC, the chart and the schematic can disagree about whether a tension is off the scale; filed as `PL-7LZ7` (whether the schematic should follow a chart's top).
