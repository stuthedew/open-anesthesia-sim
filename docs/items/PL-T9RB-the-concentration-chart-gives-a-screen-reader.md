---
id: PL-T9RB
title: The concentration chart gives a screen reader nothing: no name, no description and no text equivalent of what it plots
priority: P2
effort: M
status: needs-decision
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_chart.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no learner sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
payoff: a screen-reader user can learn what the concentration chart plots and each trace latest value
---

**Problem.** The concentration chart reaches assistive technology as two unnamed "Client" nodes (`ConcentrationChart` and pyqtgraph's `PlotWidget`) with nothing inside them. A screen-reader user learns nothing of what is plotted.

**Why it matters.** WCAG SC 1.1.1 asks non-text content that presents information, such as a chart, for a text alternative that serves the same purpose. The Understanding document's sufficient technique for a chart is a short text alternative (G95) together with a long description (G92, or G74 for one placed near the chart), and its worked example of a data chart adds that "Where possible and practical, the actual data is provided in a table" (W3C, Understanding SC 1.1.1, https://www.w3.org/WAI/WCAG21/Understanding/non-text-content, read 2026-11-23). I suggest P3.

**Approach.** Give the chart an accessible name that says what it plots and over what time window, and a description that states each drawn trace's latest value with its unit and compartment. A table of values at chosen times is the fuller answer, but the chart draws the run decimated (`docs/MODEL.md`), so a table must state the times it samples and must not imply it shows every step. Decide between the two in a design round with the run-the-app skill's screenshots. pyqtgraph draws through `QGraphicsView`, and nothing found on 2026-11-23 says it exposes its items to `QAccessible`, so the text alternative belongs on the chart widget, not on the plot items.

**How it was found.** `PL-QR6Q` built the dashboard offscreen on 2026-11-23, under PySide6 6.12, and walked the tree that `QAccessible.queryAccessibleInterface` returns for the main window, reading each node's role, name, value and description. That tree is what Qt hands to the platform's accessibility interface. It is not what a screen reader says, which `PL-H1D9` checks.

**Decision needed.** Should the chart's text alternative be a name and a description that states each trace's latest value, or a table of values at chosen times as well?

**Recommendation (provisional).** Name and description first, because they meet the short and long alternatives that SC 1.1.1's sufficient technique asks for, and a table must state the times it samples. The design round decides with the run-the-app screenshots.

**Done when.** The decision is recorded here, and a test shows the chart widget reports a name naming what it plots and its window, and a description with each drawn trace's latest value, unit and compartment.

**Priority, researched 2026-11-23.** WCAG 2.2 success criterion 1.1.1 Non-text Content is Level A: "All non-text content that is presented to the user has a text alternative that serves the equivalent purpose" (W3C, WCAG 2.2, https://www.w3.org/TR/WCAG22/, read 2026-11-23). The readouts carry the same values in text, so the chart's gap is below the P1 readout item: P2.

**Generator check.** A one-off: pyqtgraph exposes nothing to the accessibility interface, and the chart widget was given no name or description.
