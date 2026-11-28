---
id: PL-9XGQ
title: The screen-reader walk checks only that each control a reader can reach has a name, so a plot with no name or description and two controls with one name both pass it, and each is found by reading one widget (PL-T9RB, PL-R1M6, PL-YSFX)
priority: P1
effort: S
status: done
classes: defect
feature: presentation-safety
touches: tests/integration/test_keyboard_focus.py, docs/INTERFACE.md
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; its members are deferred from the same gate, and the release waits only on the owner's test drive (triage 2026-11-28)
added: 2026-11-28
closed: 2026-11-28
pr: 2359
filed-pr: 2353
payoff: a plot, a schematic or a control added later fails a test when a screen reader would get no name for it, or a name it shares with another, instead of waiting for someone to read that widget
tests: tests/integration/test_keyboard_focus.py::test_no_two_controls_a_reader_can_reach_are_said_to_be_for_the_same_thing, tests/integration/test_keyboard_focus.py::test_every_control_and_picture_in_every_workspace_reaches_a_screen_reader_named, tests/integration/test_keyboard_focus.py::test_each_painted_widget_that_draws_no_picture_still_paints
root-cause-of: PL-RK9Z, PL-T9RB, PL-R1M6, PL-YSFX
generator: spent - check: test_every_control_and_picture_in_every_workspace_reaches_a_screen_reader_named and test_no_two_controls_a_reader_can_reach_are_said_to_be_for_the_same_thing in tests/integration/test_keyboard_focus.py walk every shipped Workspace and the one with every kind of View, with one run and two, and fail on an unnamed control, a picture with no name or description of its own, an Area whose View did not build, and two controls or pictures of one role that share a name, so a View, plot or painted widget added later fails before it merges
misread: What a screen reader is told about each element: its role, and a name unique in its window
---

**Problem.** The walk in `tests/integration/test_keyboard_focus.py` (`_unnamed`, built by `PL-RK9Z`) reads the tree that Qt hands each platform's accessibility interface. It fails on a node that takes the focus and has no name, and it checks nothing else. A plot takes no focus (`test_a_plot_is_not_a_tab_stop` holds every `PlotWidget` at `Qt.FocusPolicy.NoFocus`), so a plot with no name and no description passes it. The concentration chart did until `PL-T9RB`, and the wash-in plot and the compartment schematic still do (`PL-R1M6`). The walk never compares two names, so two controls with one name pass it too. Each compared run's playback selector is "Playback", and the Induction Workspace's two window selectors are both "Time base" (`PL-YSFX`). So each gap is found only when someone happens to read that widget.

**Why it matters.** A screen-reader user who reaches an unnamed plot learns nothing of what it draws. One who reaches two controls with one name cannot tell which run or which plot the next key press changes. `PL-R1M6` and `PL-YSFX` cite the WCAG 2.2 success criteria that ask for each (1.1.1, 2.4.6 and 4.1.2, read 2026-11-27). A View or control added later carries the same risk, and no test fails on it.

**Reproduced 2026-11-28.** `_unnamed` keeps only nodes whose state is focusable (`node.state().focusable`), and no line of `tests/integration/test_keyboard_focus.py` compares the names of two nodes. In `src/anesthesia_sim/app/qt_chart.py` only the concentration chart installs an accessible interface (`_ConcentrationChartAccessible`, role `Graphic`). `WashInChart` and the schematic's widgets in `qt_schematic.py` install none.

**Approach.** Widen the one walk rather than fixing widgets one at a time. Over every shipped Workspace, with one run and with two compared, fail on a plot or schematic widget that has no name or no description, and on two visible nodes of one role in one window that have the same name. Keep the new-case question in the walk, as now. The widened test fails until `PL-R1M6`, `PL-YSFX` and `PL-XV64` (the Area corners and borders share one name, filed on the defects thread's branch on 2026-11-28) are fixed, so land it with the last of them.

**Done when.** A test walks the accessible tree of every shipped Workspace, with one run and with two compared. It fails on any plot or schematic with no name or no description, and on any two visible elements of one role in one window that share a name. It passes on `main` once `PL-R1M6`, `PL-YSFX` and `PL-XV64` are fixed.

**Generator check.** This item is the head of one fact: what a screen reader is told about each element on screen, its role and a name that tells it apart from the others in its window. Each widget's writer misread it: `PL-RK9Z` (61 controls with no name, closed 2026-11-27), `PL-T9RB` (the concentration chart, closed 2026-11-27), `PL-R1M6` and `PL-YSFX`. No head's `misread:` states it (`bin/docket generators --misread`, read 2026-11-28).

**Fix, 2026-11-28.** The walk in `tests/integration/test_keyboard_focus.py`
now covers each shipped Workspace and the one that shows every kind of View,
each with one run and with two compared. For each shipped Workspace the
branch is taken in the first one, which shows the branch control, and the
window then switches tab, as a user would. The window is large enough that
each View draws all it can show.

1. `test_no_two_controls_a_reader_can_reach_are_said_to_be_for_the_same_thing`
   now compares the pictures' names with the controls', and runs in every
   walked Workspace. Static text is left out, because its name is the text
   the screen shows in that place. Only the Workspace with every kind of View
   checks that each entry of `SHARED_PURPOSES` is still needed, because a
   shipped Workspace with one Area would have no border to share a name.
2. `test_every_control_and_picture_in_every_workspace_reaches_a_screen_reader_named`
   fails on a control a reader can reach that has no name, and on a picture
   that does not sit in an image with a name and a description of its own. A
   picture is any graphics view, which every plot is drawn in, an SVG widget,
   a label that shows only an image, a recorded picture or a movie, or any
   widget that a class of this program paints for itself. It is found among
   the widgets shown, not from a list of known classes, so a diagram added
   later on a new canvas class is in the walk. Two pictures in one image fail
   it, and so does a hidden image, an image node with no name or description,
   and an Area whose View failed to build.
3. `PAINTED_NOT_PICTURES` lists the eight classes that paint themselves but
   draw no picture, each with its reason: the Area border and corner, the
   drag preview, the two legend samples, the compartment names over the
   schematic, the focus ring and a selector's arrow.
   `test_each_painted_widget_that_draws_no_picture_still_paints` fails on an
   entry whose class is gone or no longer paints, so an entry cannot hide the
   next class given its name.

**Where it differs from the approach above.** The walk lands with `PL-XV64`'s
two exceptions still listed in `SHARED_PURPOSES`, rather than after
`PL-XV64`. Its own test fails when an entry is no longer needed, and
`PL-XV64`'s done-when already asks that both go. Landing first puts the check
on every change in the meantime.

**Regression check, 2026-11-28.** Each of three planted faults fails the
widened walk, and the walk passes without them. A wash-in plot description
of "" fails the picture test in the Workspace with every View and in the
induction Workspace, with one run and with two. A schematic name that drops
the run fails the shared-name test with two runs compared, in the Workspace
with every View and in the maintenance Workspace. Renaming the
`ContainerNames` entry fails the picture test wherever a schematic is shown,
and fails the stale-entry test. Before this change, no test in this file read
a picture's name or description. `PL-R1M6`'s own tests catch the first two
faults, but only for the widgets they name.

**Documents checked, 2026-11-28.** `docs/INTERFACE.md`: the paragraph on
controls that a screen reader can reach now says that no two controls or
pictures share a name in any shipped Workspace, and a new paragraph after the
schematic's says that every picture has a text alternative and lists the two
new tests. `docs/ARCHITECTURE.md` and `docs/VERIFICATION.md` say nothing of
this walk.

**Blind review, 2026-11-28.** Two passes, on the change alone. All findings
were fixed:

1. Pass 1, should-fix: a View that failed to build shows a notice in its
   Area, so its pictures were never walked and the test passed. The test now
   requires one built View for each Area of the layout, and at least one
   picture. With the wash-in View's constructor made to raise, the induction
   Workspace fails it.
2. Pass 1, optional, and pass 2, optional, repeated: a picture drawn by Qt's
   own widgets, such as a label given an image or an SVG widget, was not
   counted. Both are counted now, and so is every image node the accessible
   tree holds. A picture drawn onto another widget from outside it is still
   not found, and `docs/INTERFACE.md` says so.
3. Pass 1, optional, and pass 2, optional, repeated: a second picture inside
   a described image passed on that image's text. Each image may now cover
   one picture. With a second plot added inside the concentration chart, the
   default Workspace fails it with "ConcentrationChart that holds 2
   pictures".
4. Pass 2, optional: an image that takes the focus would be counted twice in
   the shared-name test and reported as sharing its name with itself. Images
   that take the focus are now counted once, as controls.
