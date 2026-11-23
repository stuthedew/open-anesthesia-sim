---
id: PL-RK9Z
title: Several controls have no name a screen reader can say, and the selectors are named only by the value they show; no test fails on an unnamed control
priority: P2
effort: M
status: ready
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_keyboard_focus.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no learner sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
payoff: every control a screen-reader user reaches says what it is for, and a new unnamed control fails a test
---

**Problem.** Several controls reach assistive technology with no name: the bookmark Instant spin box, the MAC-target Height spin box, both optional Name fields, the Area corner zones and the scroll areas. The selectors for the agent, the playback rate, the time base and the target compartment are named only by the value they show, so a screen reader says "Sevoflurane, combo box" and never "Agent". Nothing fails when a new control arrives without a name.

**Why it matters.** WCAG 2.2 success criterion 4.1.2 asks every control for a name that a program can read, and SC 1.1.1 asks a control to have "a name that describes its purpose" (W3C, Understanding SC 1.1.1, https://www.w3.org/WAI/WCAG21/Understanding/non-text-content, read 2026-11-23). I suggest P3.

**Approach.** Give each labelled control its label as a buddy (`QLabel.setBuddy`). A check on 2026-11-23 showed a buddy gives a `QSpinBox` its label's text as its accessible name. Give each selector an accessible name for its purpose. Then add a test that walks the built dashboard's accessible tree and fails on a visible, focusable node with no name, with a short list of reasoned exceptions. That test is what keeps the next control from arriving unnamed.

**How it was found.** `PL-QR6Q` built the dashboard offscreen on 2026-11-23, under PySide6 6.12, and walked the tree that `QAccessible.queryAccessibleInterface` returns for the main window, reading each node's role, name, value and description. That tree is what Qt hands to the platform's accessibility interface. It is not what a screen reader says, which `PL-H1D9` checks.

**Done when.** Each control in the list reports a name for its purpose, and a test walks the accessible tree and fails on a visible, focusable node with no name, with a short list of reasoned exceptions.

**Priority, researched 2026-11-23.** WCAG 2.2 success criterion 4.1.2 Name, Role, Value is Level A, the minimum level: "the name and role can be programmatically determined" (W3C, WCAG 2.2, https://www.w3.org/TR/WCAG22/, read 2026-11-23). These controls set no clinical value without a label, so they are below the P1 sliders, and as Level A failures above the filer's P3: P2.

**Generator check.** A one-off: no control was given an accessible name, and the test this item adds is what stops the next one.
