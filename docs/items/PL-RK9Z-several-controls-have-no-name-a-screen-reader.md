---
id: PL-RK9Z
title: Several controls have no name a screen reader can say, and the selectors are named only by the value they show; no test fails on an unnamed control
priority: P2
effort: M
status: done
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_keyboard_focus.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
closed: 2026-11-27
pr: 2333
payoff: every control a screen-reader user reaches says what it is for, and a new unnamed control fails a test
tests: tests/integration/test_keyboard_focus.py::test_every_control_a_reader_can_reach_says_what_it_is_for, tests/integration/test_keyboard_focus.py::test_each_selector_is_named_by_its_shown_label_on_every_platform
---

**Problem.** Several controls reach assistive technology with no name: the bookmark Instant spin box, the MAC-target Height spin box, both optional Name fields, the Area corner zones and the scroll areas. The selectors for the agent, the playback rate, the time base and the target compartment are named only by the value they show, so a screen reader says "Sevoflurane, combo box" and never "Agent". Nothing fails when a new control arrives without a name.

**Why it matters.** WCAG 2.2 success criterion 4.1.2 asks every control for a name that a program can read, and SC 1.1.1 asks a control to have "a name that describes its purpose" (W3C, Understanding SC 1.1.1, https://www.w3.org/WAI/WCAG21/Understanding/non-text-content, read 2026-11-23). I suggest P3.

**Approach.** Give each labelled control its label as a buddy (`QLabel.setBuddy`). A check on 2026-11-23 showed a buddy gives a `QSpinBox` its label's text as its accessible name. Give each selector an accessible name for its purpose. Then add a test that walks the built dashboard's accessible tree and fails on a visible, focusable node with no name, with a short list of reasoned exceptions. That test is what keeps the next control from arriving unnamed.

**How it was found.** `PL-QR6Q` built the dashboard offscreen on 2026-11-23, under PySide6 6.12, and walked the tree that `QAccessible.queryAccessibleInterface` returns for the main window, reading each node's role, name, value and description. That tree is what Qt hands to the platform's accessibility interface. It is not what a screen reader says, which `PL-H1D9` checks.

**Done when.** Each control in the list reports a name for its purpose, and a test walks the accessible tree and fails on a visible, focusable node with no name, with a short list of reasoned exceptions.

**Priority, researched 2026-11-23.** WCAG 2.2 success criterion 4.1.2 Name, Role, Value is Level A, the minimum level: "the name and role can be programmatically determined" (W3C, WCAG 2.2, https://www.w3.org/TR/WCAG22/, read 2026-11-23). These controls set no clinical value without a label, so they are below the P1 sliders, and as Level A failures above the filer's P3: P2.

**Generator check.** A one-off: no control was given an accessible name, and the test this item adds is what stops the next one.

**Built 2026-11-27.** `qt_widgets.label_control` ties a shown label to its control as the control's buddy and sets the control's accessible name. Every field and selector the item lists now goes through it: the bookmark editor's five fields, the price form's fields, both chart Views' time base selectors, the cost unit selector, the playback rate and the agent selector. The two "Name" fields and the two "Add" buttons are named with their form's kind of mark (`dashboard_frame.form_control_name`), and the branch point list is "From, branch point". Each scroll box that takes the focus is named, the run's list of control changes by its heading. The Area corner is named "Area corner" and describes the Area menu as the keyboard route. The walk needed no exceptions.

**Why a buddy and not only a name, checked at source 2026-11-27.** Qt 6.12's `QAccessibleComboBox::text` (`src/widgets/accessible/complexwidgets.cpp`, read from the Qt 6.12 source) returns the current entry as the name on `Q_OS_UNIX`, which covers Linux and macOS, and the accessible name only on Windows. On macOS, `qcocoaaccessibilityelement.mm` reports the first `Label` relation as `AXTitleUIElement`, and Qt adds that relation for a `QLabel` buddy (`qaccessiblewidget.cpp`, `qlabel.cpp`). So `setAccessibleName` alone leaves a selector named "Sevoflurane" on two of the three platforms, and the buddy is what reaches them.

**Decision, 2026-11-27: the agent selector gains a shown "Agent" caption.** A buddy is a label on screen, so a selector with none cannot have one. The W3C tutorial "Labeling Controls" (https://www.w3.org/WAI/tutorials/forms/labels/, read 2026-11-27) opens "Provide labels to identify all form controls, including text fields, checkboxes, radio buttons, and drop-down menus", and WCAG 2.2 SC 3.3.2 (Level A) asks that "Labels or instructions are provided when content requires user input" (https://www.w3.org/TR/WCAG22/, read 2026-11-27). The same row already shows "Playback" before the playback rate, so the caption copies that style. The Understanding document for SC 2.5.3 says "A best practice is to have the text of the label at the start of the name" (https://www.w3.org/WAI/WCAG22/Understanding/label-in-name, read 2026-11-27), which is why every combined name starts with the shown label.

**Regression run, 2026-11-27.** The two new tests in `tests/integration/test_keyboard_focus.py`, copied into a scratch module and run against the tree before the fix with `uv run pytest -q tests/integration/test_rk9z_before.py`, failed: `assert _unnamed(dashboard) == []` with "Left contains 61 more items, first extra item: 'Client QScrollArea'", and `assert AGENT_SELECTOR_LABEL in labels` with "assert 'Agent' in {''}".

**Docs swept.** `docs/INTERFACE.md` § "Color contrast, and the standard this interface is held to" gains the requirement. `docs/ARCHITECTURE.md`, `README.md` and `docs/MODEL.md` say nothing about accessible names and needed no change.
