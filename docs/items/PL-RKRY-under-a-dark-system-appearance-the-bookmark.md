---
id: PL-RKRY
title: Under a dark system appearance the bookmark dialog's entries, spin boxes and lists render the host's near-black surfaces, because no widget in either dialog declares a palette
priority: P2
effort: S
status: done
classes: defect, ux
feature: platform-palette
touches: src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_dark_appearance.py, tools/contrast_check.py, docs/MODEL.md, docs/ARCHITECTURE.md, .claude/rules/ui-color.md
added: 2026-09-20
closed: 2026-09-20
pr: 762
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
sub-controls and recolours them.

**One measured correction, recorded because it was believed for an hour and is
the kind of thing a later session re-derives.** A first attempt built the
palette with a default-constructed `QPalette()` and overrode the roles that
carry meaning, and an *unchecked* check box then rendered as a solid dark
square. That was read as the bevel roles - `Mid`, `Dark`, `Shadow` - coming
from the host, and it is not: bisecting them one at a time changes nothing, and
a palette built from the widget's *own* palette with only the ten meaning roles
written renders the indicator correctly. PySide6's `QPalette()` is not the
application's palette, which is where the dark square came from.

That is what makes the fix admissible under the disabled-colour rule.
`declare_interface_colours` starts from the widget's palette and writes the
`Active` and `Inactive` colour groups only, so the `Disabled` group stays
exactly as the platform supplied it - no second declared disabled colour, which
`.claude/rules/ui-color.md` makes a decision rather than a style choice, and
`tests/integration/test_dark_appearance.py` holds it role by role on a widget
that is actually disabled.

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


**What the work changed in the check, and why that is a narrowing rather than a
hole.** `check_authored_disabled_colours_are_measured` refused `setPalette`
outright, on the reasoning that a palette assigned wholesale carries the
`Disabled` group with it and leaves no pair a requirement could name. That
premise does not cover these controls: a spin box's stepper and a check box's
indicator are painted from palette roles no stylesheet reaches, so refusing the
mechanism outright would have meant leaving them the host's near-black. The
refusal is now on the same terms as the `:disabled` admission beside it - a
`setPalette` is admitted only from a function some requirement cites by name,
and refused everywhere else - and the part that is not decidable by reading the
tree moved to a test that checks the property directly. The check's own unit
tests still pass unchanged, including the one holding an uncited `setPalette`
to an error.
