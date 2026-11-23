---
id: PL-N5JB
title: A screen reader reaches each readout value as a bare number with its unit, without the compartment it belongs to or that it is a modelled value
priority: P1
effort: M
status: done
classes: defect, safety
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_qt_widgets.py, tests/integration/simulation_view/test_simulation_view_readouts.py, tests/unit/test_dashboard_frame.py, docs/INTERFACE.md
added: 2026-11-23
closed: 2026-11-23
pr: 2312
payoff: a screen-reader user hears each readout value with its compartment and that it is modelled
tests: tests/integration/simulation_view/test_simulation_view_readouts.py::test_a_screen_reader_hears_each_reading_with_its_compartment_and_that_it_is_modelled, tests/integration/simulation_view/test_simulation_view_readouts.py::test_a_compared_run_s_readings_are_named_with_their_run, tests/unit/test_dashboard_frame.py::test_each_reading_is_named_with_its_compartment_and_that_it_is_modelled, tests/unit/test_dashboard_frame.py::test_a_withheld_reading_is_named_in_words_not_by_its_dash, tests/unit/test_dashboard_frame.py::test_every_compartment_readout_is_marked_modelled_and_the_clock_is_not
---

**Problem.** Each readout panel (Circuit, Alveolar, Mixed venous, Vessel-rich group, Muscle and Fat) reaches assistive technology as an unnamed group of separate labels: the compartment name, its gloss, the percent ("0.00%") and the multiple of MAC ("0.00 ×MAC"). A screen reader that moves by item, or that reads a value on its own, says "0.00 percent" with nothing to say which compartment it belongs to, or that it is a modelled value and not a measurement. The clock panel has the same shape ("0s", "1× real time").

**Why it matters.** `CLAUDE.md`'s safety standard counts a value shown without its patient context, or a predicted value that could be taken for a measurement, as a safety failure. Here the context is on screen but not in what a screen reader reaches. I suggest P1 for that reason.

**Approach.** Give each `MetricPanel` an accessible name that names the compartment and says the values are modelled, and give each value label a name that carries its compartment, for example "Alveolar, modelled: 1.20%". Build that text from the strings the panel already shows, so it cannot drift from them. Update it whenever the value changes, and send a `QAccessibleValueChangeEvent` or text-change event so a screen reader that is reading the panel hears the new value. Test it with the accessible-tree walk.

**How it was found.** `PL-QR6Q` built the dashboard offscreen on 2026-11-23, under PySide6 6.12, and walked the tree that `QAccessible.queryAccessibleInterface` returns for the main window, reading each node's role, name, value and description. That tree is what Qt hands to the platform's accessibility interface. It is not what a screen reader says, which `PL-H1D9` checks.

**Done when.** A test walks the accessible tree and shows that each readout value's accessible text names its compartment and says it is modelled, built from the strings the panel shows, and that it changes when the value changes.

**Priority, researched 2026-11-23.** WCAG 2.2 success criterion 4.1.2 Name, Role, Value is Level A, the minimum level (W3C, WCAG 2.2, https://www.w3.org/TR/WCAG22/, read 2026-11-23). A value reached without its compartment, or that could be taken for a measurement, is what the safety standard counts as a safety failure, so P1.

**Generator check.** A one-off: each panel is a group of separate labels, and no accessible name joins them.

**Reproduced 2026-11-23** by `PL-QR6Q`'s walk of the accessible tree, the same day.

**Done 2026-11-23.** Each line of a readout panel that carries a reading, the value and the second line, now has an accessible name built by `spoken_reading` in `src/anesthesia_sim/app/dashboard_frame.py` from the strings the panel shows: the panel's name and its gloss, ", modelled" for a compartment, the reading, and the run's name first while runs are compared. Examples are "Alveolar, end-tidal-equivalent, modelled: 1.20%" and "Run 2, Alveolar, end-tidal-equivalent, modelled: 1.20%". The clock is not modelled, so it reads "Simulated time: 0s". `Readout.modelled` is read from the panel it is drawn on. `MetricPanel` rewrites a name only when it changes, and Qt tells assistive technology of each change. The approach named a value-change event. None was added, because `QWidget::setAccessibleName` already sends a name-change event whenever the name differs (qtbase 6.10, `src/widgets/kernel/qwidget.cpp`, read 2026-11-23). `docs/INTERFACE.md` states the requirement. Run against the code before the fix, the accessible-tree test fails at its first panel with `AssertionError: assert '0s' == 'Simulated time: 0s'`, and the compared-runs test with `assert '0s' == 'Run 1, Simulated time: 0s'`. Docs checked: `docs/INTERFACE.md`, `docs/MODEL.md`, `README.md`.

**Review, 2026-11-23.** Both blind review passes found that a withheld reading, shown as a dash after a halt with no new frame, was named with the dash, such as "Alveolar, modelled: —%". On screen the dash says the value is withheld by how it looks, so a screen reader is now told in words, such as "Circuit, inspired, modelled: percent not shown" (`SPOKEN_WITHHELD_READINGS`). `test_a_withheld_reading_is_named_in_words_not_by_its_dash` fails on the earlier code with `assert 'Circuit, modelled: —%' == 'Circuit, inspired, modelled: percent not shown'`. The first pass also found that the name left out the panel's gloss, so "Circuit, modelled: 2.00%" could be taken for the vaporizer setting; the gloss now follows the name. The second pass found that `Readout.modelled` was a second copy of `ReadoutPanel.is_clock`, set by hand by each builder. `Readout` now carries its `ReadoutPanel`, and `modelled` is read from it.

