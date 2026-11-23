---
id: PL-N5JB
title: A screen reader reaches each readout value as a bare number with its unit, without the compartment it belongs to or that it is a modelled value
priority: P1
effort: M
status: ready
classes: defect, safety
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_qt_widgets.py
added: 2026-11-23
payoff: a screen-reader user hears each readout value with its compartment and that it is modelled
---

**Problem.** Each readout panel (Circuit, Alveolar, Mixed venous, Vessel-rich group, Muscle and Fat) reaches assistive technology as an unnamed group of separate labels: the compartment name, its gloss, the percent ("0.00%") and the multiple of MAC ("0.00 ×MAC"). A screen reader that moves by item, or that reads a value on its own, says "0.00 percent" with nothing to say which compartment it belongs to, or that it is a modelled value and not a measurement. The clock panel has the same shape ("0s", "1× real time").

**Why it matters.** `CLAUDE.md`'s safety standard counts a value shown without its patient context, or a predicted value that could be taken for a measurement, as a safety failure. Here the context is on screen but not in what a screen reader reaches. I suggest P1 for that reason.

**Approach.** Give each `MetricPanel` an accessible name that names the compartment and says the values are modelled, and give each value label a name that carries its compartment, for example "Alveolar, modelled: 1.20%". Build that text from the strings the panel already shows, so it cannot drift from them. Update it whenever the value changes, and send a `QAccessibleValueChangeEvent` or text-change event so a screen reader that is reading the panel hears the new value. Test it with the accessible-tree walk.

**How it was found.** `PL-QR6Q` built the dashboard offscreen on 2026-11-23, under PySide6 6.12, and walked the tree that `QAccessible.queryAccessibleInterface` returns for the main window, reading each node's role, name, value and description. That tree is what Qt hands to the platform's accessibility interface. It is not what a screen reader says, which `PL-H1D9` checks.

**Done when.** A test walks the accessible tree and shows that each readout value's accessible text names its compartment and says it is modelled, built from the strings the panel shows, and that it changes when the value changes.

**Priority, researched 2026-11-23.** WCAG 2.2 success criterion 4.1.2 Name, Role, Value is Level A, the minimum level (W3C, WCAG 2.2, https://www.w3.org/TR/WCAG22/, read 2026-11-23). A value reached without its compartment, or that could be taken for a measurement, is what the safety standard counts as a safety failure, so P1.

**Generator check.** A one-off: each panel is a group of separate labels, and no accessible name joins them.

**Reproduced 2026-11-23** by `PL-QR6Q`'s walk of the accessible tree, the same day.
