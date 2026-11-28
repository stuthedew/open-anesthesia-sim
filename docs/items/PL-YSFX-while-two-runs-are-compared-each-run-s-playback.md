---
id: PL-YSFX
title: While two runs are compared, each run's playback selector reaches a screen reader as "Playback" alone, and in the Induction Workspace both plots' window selectors are "Time base" alone, so a screen-reader user cannot tell which run or plot a selector sets
priority: P3
effort: S
status: done
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/views.py, tests/integration/test_keyboard_focus.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/branch_controls.py, src/anesthesia_sim/app/qt_agent_price.py, src/anesthesia_sim/app/view_registry.py, tests/integration/approved_interface_strings.json, docs/INTERFACE.md, docs/items/PL-XV64-every-area-corner-reaches-a-screen-reader-as.md
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it; each selector is named and only the run or plot it sets is missing, so the release waits only on the owner test drive (filed 2026-11-27)
added: 2026-11-27
closed: 2026-11-28
pr: 2356
filed-pr: 2333
payoff: a screen-reader user who reaches a playback or time base selector hears which run or plot it sets
tests: tests/integration/test_keyboard_focus.py::test_no_two_controls_a_reader_can_reach_are_said_to_be_for_the_same_thing, tests/integration/test_keyboard_focus.py::test_each_run_s_and_each_plot_s_controls_are_named_with_their_run_or_plot, tests/integration/test_keyboard_focus.py::test_a_control_named_for_one_of_two_runs_takes_its_label_s_name_back_when_one_is_drawn, tests/integration/test_keyboard_focus.py::test_a_name_that_does_not_start_with_the_shown_label_is_refused, tests/integration/test_keyboard_focus.py::test_each_selector_is_named_by_its_shown_label_on_every_platform
recurrences: 2026-11-28 PL-XV64
---

**Problem.** `PL-RK9Z` named every control from the label shown beside it, and added which one it is where two controls in one form share a label, such as "Add, time bookmark" and "Add, MAC target". It did not do this for controls that repeat across runs or Views. While two runs are compared, each run's playback selector is named "Playback" (`RunView._lay_out_transport_row`). In the Induction Workspace the concentration chart's and the wash-in plot's window selectors are both named "Time base" (`views.py`, `label_control(time_base_name, self._window.selector)`). A screen-reader user moving through the controls hears the same name twice and cannot tell which run's playback rate, or which plot's window, the next key press changes. The run's list of control changes is already named with its run, by `compared_panel_heading` in `RunView`, so these two are the gap.

**Why it matters.** WCAG 2.2 SC 2.4.6 (Headings and Labels, Level AA) reads "Headings and labels describe topic or purpose", and SC 4.1.2 asks that each control's name can be programmatically determined (read 2026-11-27). A sighted user sees which run's panel or which plot a selector sits under. A screen-reader user gets only the name. I suggest P3, because each selector is named and only the run or plot is missing.

**Approach.** Add the run's name to the playback selector's accessible name while two runs are drawn, as `compared_panel_heading` adds it to the control timeline's heading, and add the plot's heading to each window selector's name. Keep the shown label at the start of each name, which the Understanding document for SC 2.5.3 (Label in Name) calls best practice: "Playback, Run 2", "Time base, wash-in". The names are written by `dashboard_frame` with the other control names, so the interface wording test approves them.

**Done when.** A test with two compared runs reads two different names for the two playback selectors, and a test of the Induction Workspace reads two different names for the two window selectors.

**How it was found.** The first independent review of `PL-RK9Z`'s change, 2026-11-27, as an optional finding.

**Reproduced 2026-11-28.** `src/anesthesia_sim/app/views.py` names both window selectors with `label_control(time_base_name, self._window.selector)`, and nothing adds the plot's heading. No test in `tests/integration/test_keyboard_focus.py` compares the names of two controls.

**Decided 2026-11-28.** The brief's names are the ones the sources
support, so they are taken without a question. The W3C's ARIA Authoring
Practices Guide (in its section "Composing Effective and User-friendly Accessible Names",
https://www.w3.org/WAI/ARIA/apg/practices/names-and-descriptions/, read
2026-11-28) asks for "unique names for elements with the same role unless the
elements are actually identical", says "Be concise. For many elements, one to
three words is sufficient", and puts the most distinguishing words first. The
Understanding document for WCAG 2.2 SC 2.5.3 asks that the name start with the
label shown. So each name is the label, then the run's name or the View's
title as the View chooser shows it: "Playback, Run 2", "Time base, Wash-in".
A View's title is short where its heading is a sentence, so the title is the
one used.

**What building it found.** Two things the brief did not say. First, the
brief's route would have fixed Windows only. Qt names a selector on Linux and
macOS by the entry it shows, and takes its purpose from the tied label alone
(`qt_widgets.label_control`), so a selector's own accessible name never reaches
VoiceOver. Measured here: a combo box given the accessible name "Playback, Run
2" still reports its shown entry, "1x", as its name, and the label relation reports the label's
accessible name once the label has one. So `label_control` now gives a
qualified name to the label as well, which also mends "From, branch point" and
the two "Name, ..." fields on those platforms. Second, the same gap reached
more controls than the brief names. With every kind of View on screen, each
run's Start, Pause and Reset buttons and agent selector, each plot's arrow
buttons, its "Follow the run" button and its "Axis top" selector, and the price
form's "Agent" field
shared a name with another control. Each is named the same way here. The Area
corners and borders share names too, and `PL-XV64` holds them.

**Fix.** `dashboard_frame.control_name` is the one grammar for such a name,
and replaces `form_control_name`; `branch_controls.FORK_POINT_KIND` replaces
the branch point's own copy of it. The titles of the three Views that draw
against an axis are `dashboard_frame` constants, which the View registry and
the Views both read. `views._TimeWindow` takes its View's title and names its
selector and buttons with it, and `_labelled_control` takes the title for each
axis control. `RunView._show_name` names the agent selector, the playback
selector and the three run buttons with the run on each frame, and back to
the label alone when one run is drawn. `label_control` writes only a name that
differs, so a name written again on each frame sends a screen reader no
change.

**Generator check, 2026-11-28.** Triage (`#2353`) records this item as a
member of `PL-9XGQ`, whose `misread:` states the fact: what a screen reader is told
about each element, its role and a name unique in its window. This item
builds the half of that head's fix that compares two names.
`test_no_two_controls_a_reader_can_reach_are_said_to_be_for_the_same_thing`
fails on two controls that share a name. The exceptions it lists are
`PL-XV64`'s. That test builds each kind of View once, so it cannot see the
plot controls of two Areas that show the same kind of View, which a split
makes. `PL-XV64` holds that case too, and its "Done when" adds a split layout
to the test. `PL-9XGQ` still owns the walk's other half, a plot or a
schematic with no name or description.

**Tests.** In `tests/integration/test_keyboard_focus.py`:
`test_no_two_controls_a_reader_can_reach_are_said_to_be_for_the_same_thing`
(with one run and with two compared, every kind of View on screen, against the
table `SHARED_PURPOSES`, which is checked in both directions),
`test_each_run_s_and_each_plot_s_controls_are_named_with_their_run_or_plot`
(the brief's "Done when", against literal names), and
`test_a_control_named_for_one_of_two_runs_takes_its_label_s_name_back_when_one_is_drawn`
and `test_a_name_that_does_not_start_with_the_shown_label_is_refused`.
`test_each_selector_is_named_by_its_shown_label_on_every_platform` now
compares each selector's name with the text its label shows, because the
label's accessible name is now the selector's own name.

**Regression check.** The first two tests, with the third test and the two new
imports taken out of a copy of the file, were run against `origin/main`
(aa4dca79) with `QT_QPA_PLATFORM=offscreen PYTHONPATH=<main's src> python -m
pytest -q <copy> -k "same_thing or named_with_their_run"`. All three cases
failed: with one run, "Left contains 6 more items, first extra item:
('Button', 'Show a later part of the run')"; with two runs, "Left contains 9
more items, first extra item: ('Button', 'Pause')"; and "At index 0 diff:
'Playback' != 'Playback, Run 1'".
The refusal test was run against this branch's code before the refusal was
added (63151ef3), and failed with "DID NOT RAISE ValueError".

**Blind review, 2026-11-28.** Two passes. Both found one should-fix: a split
gives two Areas of the same kind of View, so their plot controls share names,
and the new sentence in `docs/INTERFACE.md` was false for that layout. It is
filed into `PL-XV64`, whose Area names fix the corners, the borders and this
case together, and the sentence now lists it among the cases still to be
named apart. Pass 1 found a second should-fix:
`test_each_selector_is_named_by_its_shown_label_on_every_platform` compared
each selector's name with its label's accessible name, which this change makes
the selector's own name, so the test could no longer fail. Fixed: the test
reads the label's shown text, and `label_control` refuses a name that does not
start with it.

**Documents checked, 2026-11-28.** `docs/INTERFACE.md` § "Color contrast,
and the standard this interface is held to" now gives the run and plot names and the three cases
still shared, which `PL-XV64` holds. `docs/ARCHITECTURE.md` § "Where new code
belongs" (a new panel or control goes in three places) and its paragraph on
how `run_view.py` and `simulation_view.py` read a run, and its note that
`app/view_registry.py` is the one list of View kinds, are still true: the
View titles moved into `dashboard_frame` constants that the registry reads,
and the registry is still the list. `docs/interface-provenance.md`'s
paragraph on the registry is still true for the same reason.
