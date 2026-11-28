---
id: PL-26K2
title: On macOS, VoiceOver reads a widget's description in place of its name, so controls and the two plots are announced without what their names say
priority: P2
effort: M
status: done
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/app/qt_schematic.py
added: 2026-11-28
closed: 2026-11-28
pr: 2364
payoff: a VoiceOver user on a Mac hears each control by its name, and each plot with its window and its Area
tests: tests/integration/test_keyboard_focus.py::test_a_control_s_hint_is_its_description_except_on_macos_where_it_is_its_help, tests/integration/test_keyboard_focus.py::test_on_macos_no_widget_is_described_by_less_than_its_name, tests/integration/simulation_view/test_simulation_view_charts.py::test_on_macos_each_compared_schematic_s_description_opens_with_its_own_run_and_instant
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

**Direction, as built (2026-11-28).** `description_is_read_as_the_name` in `app/qt_widgets.py` is the one place that says which platform reads a description in place of the name, and `name_control` there gives every affected control its name and hint by that rule. On macOS, a control that has a hint, a tool tip or a placeholder is described by its own name, and the hint goes in its help text, which Qt reads from `whatsThis()` and the macOS bridge hands over as `accessibilityHelp`. On Windows and Linux nothing changes: the hint is the description, and a control with none is described by its tool tip or placeholder, as before. What NVDA, Narrator and Orca do with a help text in place of a description was not read, which is why the other platforms keep the description. A picture's description on macOS opens with its name and a full stop (`DescribedGraphic.accessible_description`). `label_control` names every labelled control through `name_control`, so on macOS an entry field's placeholder becomes its hint. Elsewhere Qt reads the placeholder itself, as before.

**Side effect.** A widget with a help text shows it in a "What's This?" box when the user presses Shift+F1 while it has the focus (`QWidget::event` in `qwidget.cpp` at tag v6.12.0, read 2026-11-28). The help texts are set on macOS alone, so only a Mac user who presses Shift+F1 on a border, a corner, a View chooser or a name field sees one.

**Done when** each affected control is announced on macOS by its name, as the bridge's mapping shows, the description each one carries on Windows and Linux is unchanged or changed on a cited source, and a test checks every control the interface-wide name check walks.


**Fixed 2026-11-28.** `name_control` in `app/qt_widgets.py` names the View chooser, every Area border and corner, each plot's earlier, later and follow buttons, and, through `label_control`, every labelled control. On macOS (`description_is_read_as_the_name`), a control that has a hint, a tool tip or a placeholder is described by its own name, and the hint goes in its help text. Elsewhere the hint stays the description, so the approved wording list, which the offscreen platform walks, is unchanged. `DescribedGraphic.accessible_description` opens each picture's description with its name on macOS, so the plots' window and hold and each picture's Area name are heard there. The schematic's description no longer opens with the run and the instant, which `PL-2XRN` added for the same reason, because on macOS the name now opens it, and elsewhere a screen reader reads the name first. Without that change a Mac user heard the run and the instant twice. `docs/INTERFACE.md` states the rule in its own paragraph, and its schematic paragraph says the pictures now carry their names on macOS. `PL-2XRN`'s unit test of the old first line is gone, and its test of two compared runs is now `test_on_macos_each_compared_schematic_s_description_opens_with_its_own_run_and_instant`, run with each platform's rule.

**Regression check.** With `name_control`'s macOS branch set to the other platforms' rule and `accessible_description` returning the subclass's description alone, `pytest "tests/integration/test_keyboard_focus.py::test_on_macos_no_widget_is_described_by_less_than_its_name[default-two runs compared]"` fails, listing every such widget, the first being "ViewChooser 'Branch' is described as 'Choose the View this Area shows'". The test needs `description_is_read_as_the_name`, which the fix added, so that variant stands in for a run on the code before.

With `compartment_schematic.py` and `qt_schematic.py` as on `main`, `pytest tests/integration/simulation_view/test_simulation_view_charts.py -k on_macos_each_compared` fails both cases with "assert 'Run 1, at 10...mulated time.' == 'Run 2, at 5m...mulated time.'", because the description repeated the run and the instant. With `label_control` passing the placeholder as the hint on every platform, `pytest tests/integration/test_keyboard_focus.py -k hint_is_its_description` fails the Windows and Linux case with "assert 'Optional' == 'Required'".

**Not checked on a Mac.** The tests set the platform rule as it is on macOS and read what Qt's accessibility interface returns. Whether VoiceOver then reads the label alone, rather than the label and the title, rests on Apple's guide, which says a screen reader asks a button for its label. A run under VoiceOver on a Mac would confirm it.

**Blind review.** Two passes ran. Both found the same fault, and pass 1 found a second.

1. Both passes, optional: on macOS the schematic's description opened with its name and then with `PL-2XRN`'s line, so VoiceOver read the run and the instant twice. Fixed on the branch by removing that line, as above.
2. Pass 1, optional: `label_control` copied an entry field's placeholder into its description on Windows and Linux, where Qt had read the live placeholder, so a placeholder changed later would have been read stale. Fixed on the branch: the placeholder becomes the hint on macOS alone, and a test changes the placeholder after naming the field. The same pass noted that a call replaces a description that a caller set on a labelled control. No caller sets one, and `name_control`'s docstring now says that it writes all three texts.

**Docs checked.** `docs/INTERFACE.md`: the macOS paragraph and the schematic's paragraph are changed, and the paragraph on legend boxes (`PL-PN2C`) still holds. `ROADMAP.md`: the frozen-list paragraphs on `PL-2XRN` and `PL-26K2` still hold, since on macOS the schematic's description still names its run and instant, now through its name. `docs/ARCHITECTURE.md`: the lines on `compartment_schematic.py` and the wording test still hold. `docs/MODEL.md`, `docs/VERIFICATION.md`, `docs/PARAMETERS.md` and `README.md` say nothing of what a screen reader is told.
