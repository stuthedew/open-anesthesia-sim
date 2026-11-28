---
id: PL-R1M6
title: The wash-in plot and the compartment schematic give a screen reader no text alternative, as the concentration chart did before PL-T9RB
priority: P3
effort: S
status: ready
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_chart.py
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it; PL-T9RB, which it follows, was deferred from the same gate (filed 2026-11-27)
added: 2026-11-27
filed-pr: 2333
payoff: a screen-reader user can learn what the wash-in plot and the compartment schematic draw
---

**Problem.** The wash-in plot (`qt_chart.WashInChart`) and the compartment schematic reach a screen reader as plain widgets with no name and no description, so a screen-reader user learns nothing of what either draws. `PL-T9RB` gave the concentration chart a text alternative and left these two out of its scope.

**Why it matters.** WCAG 2.2 SC 1.1.1 (Non-text Content, Level A) asks each graphic that presents information for a text alternative that serves the same purpose. The W3C's worked example of a chart pairs a short name with a long description that names the type of chart and summarises its data (Understanding SC 1.1.1, https://www.w3.org/WAI/WCAG22/Understanding/non-text-content, read 2026-11-27). The wash-in View already states the current F_A/F_I reading in text beside the plot (`dashboard_frame.wash_in_state_lines`), so the gap there is smaller than the schematic's. I suggest P3.

**Approach.** Follow `PL-T9RB`'s pattern in `qt_chart.py`: an accessible interface with the role `Graphic`, installed by a factory, whose name and description are written by pure functions in `dashboard_frame.py` from the frame last drawn, when a screen reader asks for them. For the wash-in plot, the name is its heading and time window, and the description gives each run's latest F_A/F_I as `wash_in_state_lines` words it. For the schematic, the description gives each compartment's drawn height and amount as its labels state them. `PL-T9RB` decided against a table of values for the concentration chart, because the readouts already give each value in text, and the same reasoning should be checked here rather than assumed.

**Done when.** A test shows that each of the two widgets reports the role `Graphic`, a name naming what it plots, and a description with the values it draws, and a second test shows that the description follows a later frame.

**How it was found.** Building `PL-T9RB`, 2026-11-27: the same accessibility walk that found the concentration chart unnamed shows these two as unnamed client areas, which VoiceOver on macOS passes over.

**Reproduced 2026-11-28.** In `src/anesthesia_sim/app/qt_chart.py` only the concentration chart installs an accessible interface (`_ConcentrationChartAccessible`, role `Graphic`, installed by `QAccessible.installFactory`). `WashInChart` and the schematic's widgets in `src/anesthesia_sim/app/qt_schematic.py` install none and set no accessible name.

**Generator check.** A member of `PL-9XGQ`: what a screen reader is told about each element on screen. The walk that `PL-RK9Z` built checks only nodes that take the focus, and a plot takes none, so this passed it.
