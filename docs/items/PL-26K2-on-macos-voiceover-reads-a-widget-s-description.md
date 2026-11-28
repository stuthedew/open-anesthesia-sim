---
id: PL-26K2
title: On macOS, VoiceOver reads a widget's description in place of its name, so controls and the two plots are announced without what their names say
priority: P2
effort: M
status: ready
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/views.py
added: 2026-11-28
payoff: a VoiceOver user on a Mac hears each control by its name, and each plot with its window and its Area
---

**Problem.** On macOS, Qt 6.12 hands a widget's accessible description to VoiceOver as the element's label and its accessible name as the title (`src/plugins/platforms/cocoa/qcocoaaccessibilityelement.mm` at tag v6.12.0 of `qt/qtbase`, read 2026-11-28). Where a widget has no description, Qt uses its tool tip instead (`qaccessiblewidget.cpp`, the same tag). Apple's "Accessibility Programming Guide for OS X", § "The OS X Accessibility Model", says a screen reader asks a button for its label, which defaults to the button's title. Qt's bug report QTBUG-140871 (open, Qt 6.9.3, read 2026-11-28) records VoiceOver reading a Qt Quick item's description in place of its name, on macOS only. So on a Mac, each control below is announced by its description, and its name is not read.

The approved wording list, `tests/integration/approved_interface_strings.json`, gives the seven controls:

1. `ViewChooser` in `app/area_layout.py`: "Choose the View this Area shows".
2. `AreaMenu` in `app/area_layout.py`: "Split, join, swap, resize or close this Area", without the Area's name.
3. `_AreaHandle` in `app/area_layout.py`: "The arrow keys move it. Shift moves it alone. Escape puts it back.", in place of a name such as "Area border, below Concentrations".
4. `_CornerZone` in `app/area_layout.py`: "Drag it to split or join the Area. The Area menu does the same from the keyboard.", in place of a name such as "Area corner, Wash-in, bottom left".
5. `LayoutMenu` in `app/workspace_tabs.py`: "Switch, rename, duplicate or delete Workspaces".
6. and 7. Each plot's "Show an earlier part of the run" and "Show a later part of the run" buttons, built in `app/views.py`. They have no description, so Qt hands their tool tip over, which leaves out the plot's name that their accessible name adds, such as ", Concentrations".

The two plots are affected in the same way. `concentration_chart_name` and `wash_in_plot_name` in `app/dashboard_frame.py` end with the window, such as "held: not following the run", and `DescribedGraphic.accessible_name` in `app/qt_widgets.py` adds the Area's name to every picture's name, the schematic's too, while another Area shows a copy. No picture's description gives the Area's name, and neither plot's gives the window, so a Mac user is not told that a plot is held, or which copy of a picture they are on, which rule 6 of the Area naming rules in `docs/INTERFACE.md` puts in the name alone (`PL-XV64`). Each value line still names its run and its instant, so no value is heard without them (both passes of `PL-2XRN`'s blind review, 2026-11-28).

The "Duplicate the current Workspace" button is not affected, because its tool tip and its name are the same words.

**Found while building, 2026-11-28.** A walk of every widget in each shipped Workspace, with one run and with two, listed every one whose description differs from its name. It found three more:

1. Each plot's "Follow the run" button, which shows only while the window is held, is described by its tool tip as the earlier and later buttons are.
2. The two optional name fields, "Name, time bookmark" and "Name, MAC target", are described by their placeholder, "Optional". Qt 6.12's `QAccessibleLineEdit::text` reads a line edit's placeholder as its description where it has none (`simplewidgets.cpp` at tag v6.12.0, read 2026-11-28). So a Mac user heard "Optional" in place of the field's name.
3. The Area menu and the Workspace menu have no name on any platform, because Qt names a menu by its window title, which neither sets (`QAccessibleMenu::text` in `qaccessiblemenu.cpp`, the same tag). Their description is the only text a screen reader has for them on every platform, so macOS reads them as the others do, and they are left as they are.

**Why it matters.** A VoiceOver user cannot tell which border, corner or Area menu has the focus, or which plot an earlier or later button moves (WCAG 2.2 SC 4.1.2, Name, Role, Value). None of these controls shows or changes a clinical value, so it is not a `safety` item.

**Generator check.** No head states how each platform's bridge maps a widget's name, description, tool tip and help text. `PL-PN2C` and `PL-2XRN` each met the same mapping, and this is the third, so the fix puts the mapping in one place.

**Found** by `PL-2XRN`, 2026-11-28, which made each picture's description name its own run and instant and left the controls to this item.

**Direction, as built (2026-11-28).** `description_is_read_as_the_name` in `app/qt_widgets.py` is the one place that says which platform reads a description in place of the name, and `name_control` there gives every affected control its name and hint by that rule. On macOS, a control that has a hint, a tool tip or a placeholder is described by its own name, and the hint goes in its help text, which Qt reads from `whatsThis()` and the macOS bridge hands over as `accessibilityHelp`. On Windows and Linux nothing changes: the hint is the description, and a control with none is described by its tool tip or placeholder, as before. What NVDA, Narrator and Orca do with a help text in place of a description was not read, which is why the other platforms keep the description. A picture's description on macOS opens with its name and a full stop (`DescribedGraphic.accessible_description`). `label_control` names every labelled control through `name_control`, so an entry field's placeholder becomes its hint.

**Side effect.** A widget with a help text shows it in a "What's This?" box when the user presses Shift+F1 while it has the focus (`QWidget::event` in `qwidget.cpp` at tag v6.12.0, read 2026-11-28). The help texts are set on macOS alone, so only a Mac user who presses Shift+F1 on a border, a corner, a View chooser or a name field sees one.

**Done when** each affected control is announced on macOS by its name, as the bridge's mapping shows, the description each one carries on Windows and Linux is unchanged or changed on a cited source, and a test checks every control the interface-wide name check walks.
