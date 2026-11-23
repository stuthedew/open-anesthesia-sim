---
id: PL-9QY5
title: A screen reader hears each setting slider as an unnamed whole number in the slider's internal steps, such as 180 for 1.80% sevoflurane, with no name and no unit
status: untriaged
feature: presentation-safety
added: 2026-11-23
---

**Problem.** Each of the four setting sliders (fresh gas flow, delivered agent, alveolar ventilation and cardiac output) reaches assistive technology with no name. Its value is the slider's internal step count: 40 for 4.0 L/min of fresh gas, 180 for 1.80% sevoflurane, 40 for 4.0 L/min of ventilation and 50 for 5.0 L/min of cardiac output. A screen-reader user moving the delivered-agent slider hears "180", with no unit and no setting named.

**Why it matters.** This is `CLAUDE.md`'s "correct number with the wrong units" on a control that sets a clinical value, so the safety-critical standard applies. I suggest P1 for that reason.

**Approach.** Give each slider the setting's name as its accessible name, as its label already shows it. Give it the value as the label beside it shows it, with its unit, as the value a screen reader reads. A buddy or `setAccessibleName` gives the name: a check on 2026-11-23 showed `setAccessibleName` on a `QSlider` changes the name Qt reports. The value text is harder. `setAccessibleDescription` can carry the formatted value, but Qt still reports the step count as the value. The cleaner route is an accessible interface for `_SettingSlider` (`src/anesthesia_sim/app/qt_widgets.py`), installed with `QAccessible.installFactory`, whose value text is the formatted setting. PySide6 6.12 provides `installFactory`. Read the slider's value text from the same formatter the label uses, so the two cannot differ. Test it by walking the accessible tree and comparing each slider's value text with its label.

**How it was found.** `PL-QR6Q` built the dashboard offscreen on 2026-11-23, under PySide6 6.12, and walked the tree that `QAccessible.queryAccessibleInterface` returns for the main window, reading each node's role, name, value and description. That tree is what Qt hands to the platform's accessibility interface. It is not what a screen reader says, which `PL-H1D9` checks.
