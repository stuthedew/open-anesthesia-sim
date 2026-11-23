---
id: PL-9QY5
title: A screen reader hears each setting slider as an unnamed whole number in the slider's internal steps, such as 180 for 1.80% sevoflurane, with no name and no unit
priority: P1
effort: M
status: done
classes: defect, safety
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/run_surfaces.py, src/anesthesia_sim/app/views.py, tests/integration/test_qt_widgets.py, tests/integration/simulation_view/test_simulation_view_controls.py, docs/INTERFACE.md
added: 2026-11-23
closed: 2026-11-23
pr: 2311
payoff: a screen-reader user moving a setting slider hears the setting and its value with the unit, never a bare step count
tests: tests/integration/simulation_view/test_simulation_view_controls.py::test_the_accessible_tree_names_each_setting_slider_and_gives_its_value_with_the_unit, tests/integration/simulation_view/test_simulation_view_controls.py::test_each_compared_run_s_dials_name_the_run_to_a_screen_reader, tests/integration/test_qt_widgets.py::test_assistive_technology_hears_each_slider_as_its_setting_with_the_unit, tests/integration/test_qt_widgets.py::test_a_value_set_by_assistive_technology_applies_once_in_the_setting_s_unit
---

**Problem.** Each of the four setting sliders (fresh gas flow, delivered agent, alveolar ventilation and cardiac output) reaches assistive technology with no name. Its value is the slider's internal step count: 40 for 4.0 L/min of fresh gas, 180 for 1.80% sevoflurane, 40 for 4.0 L/min of ventilation and 50 for 5.0 L/min of cardiac output. A screen-reader user moving the delivered-agent slider hears "180", with no unit and no setting named.

**Why it matters.** This is `CLAUDE.md`'s "correct number with the wrong units" on a control that sets a clinical value, so the safety-critical standard applies. I suggest P1 for that reason.

**Approach.** Give each slider the setting's name as its accessible name, as its label already shows it. Give it the value as the label beside it shows it, with its unit, as the value a screen reader reads. A buddy or `setAccessibleName` gives the name: a check on 2026-11-23 showed `setAccessibleName` on a `QSlider` changes the name Qt reports. The value text is harder. `setAccessibleDescription` can carry the formatted value, but Qt still reports the step count as the value. The cleaner route is an accessible interface for `_SettingSlider` (`src/anesthesia_sim/app/qt_widgets.py`), installed with `QAccessible.installFactory`, whose value text is the formatted setting. PySide6 6.12 provides `installFactory`. Read the slider's value text from the same formatter the label uses, so the two cannot differ. Test it by walking the accessible tree and comparing each slider's value text with its label.

**How it was found.** `PL-QR6Q` built the dashboard offscreen on 2026-11-23, under PySide6 6.12, and walked the tree that `QAccessible.queryAccessibleInterface` returns for the main window, reading each node's role, name, value and description. That tree is what Qt hands to the platform's accessibility interface. It is not what a screen reader says, which `PL-H1D9` checks.

**Done when.** A test walks the built dashboard's accessible tree and shows that each of the four setting sliders reports the setting's name as its accessible name, and the value with its unit as its value text, read from the same formatter as the label beside it.

**Priority, researched 2026-11-23.** WCAG 2.2 success criterion 4.1.2 Name, Role, Value is Level A, the minimum level: "the name and role can be programmatically determined" for every interface component (W3C, WCAG 2.2, https://www.w3.org/TR/WCAG22/, read 2026-11-23). The WAI-ARIA Authoring Practices slider pattern says that when a slider's numeric value "is not user-friendly", `aria-valuetext` carries a string "that makes the slider value understandable" (W3C APG, Slider Pattern, https://www.w3.org/WAI/ARIA/apg/patterns/slider/, read 2026-11-23). A step count read as the setting is a clinical value with the wrong unit, so the safety standard sets P1.

**Generator check.** A one-off: no accessible name or value was set on any control, which `PL-RK9Z` covers for the rest; the fact is not misread elsewhere.

**Reproduced 2026-11-23** by `PL-QR6Q`'s walk of the accessible tree, the same day.

**Done 2026-11-23.** Each setting slider now has an accessible interface, installed with `QAccessible.installFactory` once the application exists. Its current, minimum, maximum and step values are in the setting's own unit, and its value text is the text the readout beside it shows, read from the one formatter `setting_value_text` in `src/anesthesia_sim/app/dashboard_frame.py`. Its accessible name is the setting's name followed by its unit, such as "Delivered agent, %", because VoiceOver on macOS reads the number and not the value text. A value set through the interface is converted back to the slider's steps and applied once. `docs/INTERFACE.md` states the requirement. Run against the code before the fix, the test of the built dashboard's accessible tree fails at its first slider with `AssertionError: assert '40' == '4.0 L/min'`. That run used a variant without the unit lookup, because the slider's `control` attribute is new: `uv run pytest "tests/integration/simulation_view/test_simulation_view_controls.py::test_the_accessible_tree_names_each_setting_slider_and_gives_its_value_with_the_unit"` on `origin/main` at 55ec4304. Docs checked: `docs/INTERFACE.md`, `README.md`, `docs/ARCHITECTURE.md`.

**Review, 2026-11-23.** Two blind review passes found three faults, all fixed in this pull request.

1. The value interface first shared one Python class with the widget interface. That class holds two C++ objects, and a call through Qt's own `interface_cast`, made with `ctypes` at the vtable slot that `dladdr` names `QAccessibleWidget::interface_cast`, returned the widget interface's address where Qt asked for the value interface's. A platform bridge calling `currentValue` would then have called another method of the widget interface. The value interface is now an object of its own, `_SettingSliderValue`, and the same call returns its address. Returning the address as a number instead crashed the process with a segmentation fault. The tests from Python could not see the fault, because Python finds the same object at either address. The slider test now asserts that the value interface is not a widget interface and holds one C++ object, which fails on the earlier code with `assert not True`.
2. With two runs compared, both rows of sliders had the same accessible names. Each slider's name now names its run, as the failure-details buttons already do. `test_each_compared_run_s_dials_name_the_run_to_a_screen_reader` fails on the earlier code with `assert 'Fresh gas flow, L/min' == 'Fresh gas flow for Run 1, L/min'`.
3. A value that is not a finite number, set by assistive technology, announced an adjustment and then raised `ValueError: cannot convert float NaN to integer`, so no value followed it. Such a value is now ignored, and a value beyond the range applies as the nearest end.

