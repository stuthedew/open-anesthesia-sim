---
id: PL-RKRY
title: Under a dark system appearance the bookmark dialog's entries, spin boxes and lists render the host's near-black surfaces, because no widget in either dialog declares a palette
priority: P2
effort: S
status: ready
classes: defect, ux
feature: platform-palette
touches: src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_dark_appearance.py, tools/contrast_check.py, docs/MODEL.md, .claude/rules/ui-color.md
added: 2026-09-20
payoff: the dialog a learner types an instant and a MAC height into stops rendering black boxes on a light dialog under a dark host
verify: grep -q 'def test_the_bookmark_dialog_draws_the_theme_rather_than_the_host_palette' tests/integration/test_dark_appearance.py
---

**Problem.** Under a dark system appearance the bookmark dialog's entries, spin boxes and lists render the host's near-black surfaces, because no widget in either dialog declares a palette

**Why it matters.** The project owner reported it from his own screen on
2026-09-20, with a screenshot: a white dialog carrying six near-black boxes.
Reproduced headless the same day by setting the palette a host in Dark
appearance supplies (`Base #1e1e1e`, `Text #ffffff`, `PlaceholderText` a
low-alpha grey) and rendering `BookmarkDialog` under the `offscreen` plugin -
the grab matches the screenshot, so the diagnosis rests on a render rather
than on a reading of the code.

Eleven widgets in the dialog paint from the palette and declare nothing:
`instant_spin` and `height_spin` with their internal line edits,
`time_label_edit` and `target_label_edit`, `time_list` and `target_list` with
their item views, and `compartment_combo` with its popup. `PL-DHBX` is the
same mechanism one control earlier, and `PL-KRZW` is the general question -
which says "nothing in the interface is waiting on it" because `PL-DHBX`
declared every colour that carried meaning. `PL-LPLD` then put six input
controls on screen, so that sentence is now false and the fix is not waiting
on the decision.

**The placeholder is the part that gets worse rather than better with a
half-fix.** Declaring a light fill without declaring `PlaceholderText` leaves
the host's light-grey hint on a white ground - the "Optional" label goes from
poor to invisible - so the roles have to be declared as a set.

**A stylesheet is the wrong mechanism here, measured rather than assumed.**
Styling `QAbstractSpinBox` and `QComboBox` through `setStyleSheet` moves them
onto `QStyleSheetStyle`, which drew both spin boxes without their up/down
steppers and the combo without its drop-down arrow - the stepper is the only
way to change the value with a mouse. A `QPalette` keeps the native
sub-controls and recolours them. `QPalette(QColor(PANEL))` is the baseline
because it derives every role Qt's styles read - including the bevel roles
`Mid`, `Dark` and `Shadow`, which no theme constant declares - from one colour
rather than from the host, so the result is deterministic under either
appearance.

**Why the dialog's own stylesheet goes.** `QDialog { background-color: PANEL }`
is what severs palette inheritance: with a stylesheet set on the parent, every
descendant resolves from the *application* palette instead, which is how the
list's own scrollbar stayed near-black in a light list even with a palette set
on the list itself. Declaring the surface as `Window` on the dialog's palette
paints the same background and lets every widget inside it - including ones
added later - inherit.

**Done when.** `BookmarkDialog` and `NewCaseDialog` declare the interface's
palette instead of a one-rule stylesheet, `tools/contrast_check.py` names the
palette as a place its measured pairs are drawn, and a test renders the dialog
under a dark host palette and holds the entries, lists and placeholder to the
theme's colours.
