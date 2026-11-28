---
id: PL-26K2
title: On macOS, VoiceOver reads a control's description in place of its name, so seven controls are announced without the Area, corner or plot they belong to
priority: P2
effort: M
status: ready
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/workspace_tabs.py, src/anesthesia_sim/app/views.py
added: 2026-11-28
payoff: a VoiceOver user on a Mac hears each layout control and each plot's earlier and later button by its name
---

**Problem.** On macOS, Qt 6.12 hands a widget's accessible description to VoiceOver as the element's label and its accessible name as the title (`src/plugins/platforms/cocoa/qcocoaaccessibilityelement.mm` at tag v6.12.0 of `qt/qtbase`, read 2026-11-28). Where a widget has no description, Qt uses its tool tip instead (`qaccessiblewidget.cpp`, the same tag). Apple's "Accessibility Programming Guide for OS X", § "The OS X Accessibility Model", says a screen reader asks a button for its label, which defaults to the button's title. Qt's bug report QTBUG-140871 (open, Qt 6.9.3, read 2026-11-28) records VoiceOver reading a Qt Quick item's description in place of its name, on macOS only. So on a Mac, each control below is announced by its description, and its name is not read.

The approved wording list, `tests/integration/approved_interface_strings.json`, gives the seven controls:

1. `ViewChooser` in `app/area_layout.py`: "Choose the View this Area shows".
2. `AreaMenu` in `app/area_layout.py`: "Split, join, swap, resize or close this Area", without the Area's name.
3. `_AreaHandle` in `app/area_layout.py`: "The arrow keys move it. Shift moves it alone. Escape puts it back.", in place of a name such as "Area border, below Concentrations".
4. `_CornerZone` in `app/area_layout.py`: "Drag it to split or join the Area. The Area menu does the same from the keyboard.", in place of a name such as "Area corner, Wash-in, bottom left".
5. `LayoutMenu` in `app/workspace_tabs.py`: "Switch, rename, duplicate or delete Workspaces".
6. and 7. Each plot's "Show an earlier part of the run" and "Show a later part of the run" buttons, built in `app/views.py`. They have no description, so Qt hands their tool tip over, which leaves out the plot's name that their accessible name adds, such as ", Concentrations".

The "Duplicate the current Workspace" button is not affected, because its tool tip and its name are the same words.

**Why it matters.** A VoiceOver user cannot tell which border, corner or Area menu has the focus, or which plot an earlier or later button moves (WCAG 2.2 SC 4.1.2, Name, Role, Value). None of these controls shows or changes a clinical value, so it is not a `safety` item.

**Generator check.** No head states how each platform's bridge maps a widget's name, description, tool tip and help text. `PL-PN2C` and `PL-2XRN` each met the same mapping, and this is the third, so the fix puts the mapping in one place.

**Found** by `PL-2XRN`, 2026-11-28, which made each picture's description name its own run and instant and left the controls to this item.

**Direction.** One helper in `app/qt_widgets.py` gives a control its extra words, and every control above calls it. On macOS, the words belong in the help text, which Qt fills from `whatsThis()` and the bridge hands over as `accessibilityHelp`, so that the label is empty and VoiceOver reads the name. The earlier and later buttons need their label to be their name on macOS. What NVDA, Narrator and Orca do with a widget's help text, compared with its description, has not been read, so Windows and Linux keep the description until a source settles it. A test fails where a control's description on macOS differs from its name.

**Done when** each of the seven controls is announced on macOS by its name, as the bridge's mapping shows, the description each one carries on Windows and Linux is unchanged or changed on a cited source, and a test checks every control the interface-wide name check walks.
