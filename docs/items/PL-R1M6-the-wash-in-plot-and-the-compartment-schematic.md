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
recurrences: 2026-11-28 PL-MP1X
---

**Problem.** The wash-in plot (`qt_chart.WashInChart`) and the compartment schematic reach a screen reader as plain widgets with no name and no description, so a screen-reader user learns nothing of what either draws. `PL-T9RB` gave the concentration chart a text alternative and left these two out of its scope.

**Why it matters.** WCAG 2.2 SC 1.1.1 (Non-text Content, Level A) asks each graphic that presents information for a text alternative that serves the same purpose. The W3C's worked example of a chart pairs a short name with a long description that names the type of chart and summarises its data (Understanding SC 1.1.1, https://www.w3.org/WAI/WCAG22/Understanding/non-text-content, read 2026-11-27). The wash-in View already states the current F_A/F_I reading in text beside the plot (`dashboard_frame.wash_in_state_lines`), so the gap there is smaller than the schematic's. I suggest P3.

**Approach.** Follow `PL-T9RB`'s pattern in `qt_chart.py`: an accessible interface with the role `Graphic`, installed by a factory, whose name and description are written by pure functions in `dashboard_frame.py` from the frame last drawn, when a screen reader asks for them. For the wash-in plot, the name is its heading and time window, and the description gives each run's latest F_A/F_I as `wash_in_state_lines` words it. For the schematic, the description gives each compartment's drawn height and amount as its labels state them. `PL-T9RB` decided against a table of values for the concentration chart, because the readouts already give each value in text, and the same reasoning should be checked here rather than assumed.

**Done when.** A test shows that each of the two widgets reports the role `Graphic`, a name naming what it plots, and a description with the values it draws, and a second test shows that the description follows a later frame.

**How it was found.** Building `PL-T9RB`, 2026-11-27: the same accessibility walk that found the concentration chart unnamed shows these two as unnamed client areas, which VoiceOver on macOS passes over.

**Reproduced 2026-11-28.** In `src/anesthesia_sim/app/qt_chart.py` only the concentration chart installs an accessible interface (`_ConcentrationChartAccessible`, role `Graphic`, installed by `QAccessible.installFactory`). `WashInChart` and the schematic's widgets in `src/anesthesia_sim/app/qt_schematic.py` install none and set no accessible name.

**Generator check.** A member of `PL-9XGQ`: what a screen reader is told about each element on screen. The walk that `PL-RK9Z` built checks only nodes that take the focus, and a plot takes none, so this passed it.

**Fix, 2026-11-28.** `qt_widgets.DescribedGraphic` is now the one base for a
picture with a text alternative. It reports the role `Graphic`, reads its name
and description from two methods each subclass defines, and tells assistive
technology when either changes. The concentration chart, the wash-in plot
and the schematic's canvas are its three subclasses, so the concentration
chart's own accessible class and factory are gone. The wash-in plot's name is
its heading without subscript markup, then the time axis's caption. Its
description names the type, says the values are modelled, gives the last
point each run's trace draws with its instant
(`chart_frame.latest_wash_in_lines`, worded as the hover words it), and ends
with the equilibrium line. The schematic's name is the View's title, the run
while runs are compared, and the instant. Its description names the picture
and its joins, says the values are modelled, gives both units, then every
line under every container and each caption, one line each
(`compartment_schematic.schematic_description`). A dash on screen is said in
words, as the readouts say it. The canvas takes what it paints and what it
describes in one call, `SchematicCanvas.show_schematic`, so the two cannot
come from different snapshots.

**Where it differs from the approach above.** The approach had the wash-in
description give each run's line as the row above the plot words it. That
row reads the run at its present instant, which a held window does not draw,
so the description gives the last drawn point instead, as the concentration
chart's does. The row is text a screen reader already reads.

**The table question, checked.** `PL-T9RB` gave the concentration chart no
table because its readouts already give each value in text. That holds for
the wash-in plot, whose ratio is in the row above it. It does not hold for
the schematic: each compartment's amount and share appear nowhere else in
text. The W3C's tutorial on complex images
(https://www.w3.org/WAI/tutorials/images/complex/, read 2026-11-28) says a
long description is read as one block, without a table's structure, so the
description gives every value on lines that each name their own compartment.

**Regression check.** The five integration tests were run against the code
before this change (`14ad0bac`), in a copy of
`tests/integration/simulation_view/test_simulation_view_charts.py` with
`DescribedGraphic` replaced by `QWidget`, because the class did not exist
yet: `QT_QPA_PLATFORM=offscreen PYTHONPATH=src:. python -m pytest -q <copy> -k
"wash_in_plot or schematic or described_image or held_wash_in"`. All five
failed. The plot and the canvas reported "Role.Client" where "Role.Graphic"
was expected, the held plot's name was empty, no text change was reported,
and the walk failed on "PlotWidget". The review fixes' four tests were run
against this branch before those fixes (`7f0f1232`), and all four failed:
"Now: FA/FI = 0.86" where the ratio at 45m was expected, and "—%, — mL
vapour, — of agent" where the words were expected.

**Blind review, 2026-11-28.** Two passes. Both found the same should-fix: the
wash-in description gave the present reading, which a held window does not
draw. Fixed, as above. Pass 1 found a second should-fix: a withheld
schematic's text gave bare dashes, which the readouts already say in words.
Fixed. Pass 1's optional finding, that the canvas took its readings and its
description in two calls, is fixed too. Pass 2 noted that the description
says nothing of a preview, which the concentration chart's leaves out too.
That is filed as `PL-MP1X`. Building this found that the wording test reads
none of these texts, filed as `PL-96MX`.

**Documents checked, 2026-11-28.** `docs/INTERFACE.md`, the wash-in plot's
and the schematic's paragraphs, which now say what a screen reader hears from
each, and § "Color contrast, and the standard this interface is held to".
`docs/ARCHITECTURE.md`'s file tree, whose lines for `dashboard_frame.py` and
`compartment_schematic.py` now say that each writes a screen reader's name and
description, and whose lines for `qt_chart.py` and `qt_schematic.py` still
hold, because neither formats a value. `docs/VERIFICATION.md` names
accessibility only as the WCAG 2.2 AA bar, which this change meets more of.
`docs/MODEL.md` and `docs/PARAMETERS.md` describe no text a screen reader
hears.
