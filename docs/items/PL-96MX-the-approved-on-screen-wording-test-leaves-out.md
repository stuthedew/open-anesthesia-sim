---
id: PL-96MX
title: The approved on-screen wording test leaves out what a screen reader hears from each chart and diagram, their names and long descriptions, so a change of that wording passes it unread
priority: P3
effort: S
status: done
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_interface_wording.py, tests/integration/approved_interface_strings.json, tests/integration/simulation_view/test_simulation_view_whole_interface.py, docs/INTERFACE.md, docs/ARCHITECTURE.md, docs/items/PL-596J-the-concentration-chart-s-text-alternative.md
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it; each description has its own tests and only the hand check of a later change is missing, so the release waits only on the owner test drive (filed 2026-11-28)
added: 2026-11-28
closed: 2026-11-28
pr: 2360
payoff: a change to what a screen reader hears from a chart, a diagram or a control is read by hand before it merges, as on-screen wording is
tests: tests/integration/test_interface_wording.py::test_a_changed_line_that_only_a_screen_reader_hears_differs_from_the_approved_list, tests/integration/test_interface_wording.py::test_a_line_dropped_from_a_description_differs_where_the_screen_shows_the_same_words, tests/integration/simulation_view/test_simulation_view_whole_interface.py::test_what_a_screen_reader_alone_is_told_is_held_but_not_seen
---

**Problem.** `tests/integration/test_interface_wording.py` holds every string the dashboard shows to a list checked by hand (`approved_interface_strings.json`). It reads them through `SimulationView.interface_strings`, which collects each widget's shown text and a button's accessible name. It does not collect what a screen reader is told by an accessible interface: the name and long description of the concentration chart (`PL-T9RB`), of the wash-in plot and of each run's schematic (`PL-R1M6`), nor a selector's or a label's accessible name. A change to any of those sentences passes the wording test without anyone reading it.

**Why it matters.** Each of these sentences states clinical values in words, such as "Modelled sevoflurane at 10m: Circuit (inspired) 1.45%, 0.81 ×MAC", and says that they are modelled. A screen-reader user reads them in place of the picture, so a wrong label or a dropped "Modelled" there is the same presentation fault as on screen (`CLAUDE.md` § "Safety-critical clinical-output standard"). I suggest P3, because each sentence has its own tests and only the hand check of a later change is missing.

**Approach.** Have `SimulationView.interface_strings` also yield, for each widget, the name and description its accessible interface returns where they differ from the widget's shown text, split into lines as the descriptions are written. Then rerun the wording test, read the new strings and add them to the approved list.

**Done when.** The approved list holds the charts' and the schematic's names and description lines, and a test shows that a changed description line fails the wording test.

**How it was found.** Building `PL-R1M6`, 2026-11-28: its new descriptions passed the wording test without changing the approved list.

**Generator check.** No head states the fact misread here, which is which strings the wording test reads. `SimulationView.interface_strings` collects shown text and a button's accessible name, so a string given only to assistive technology is outside it. This is the first item to name the gap.

**Fixed 2026-11-28.** `SimulationView.interface_strings` now also yields, for each widget, the name and the description that its accessible interface returns, one string for each line, wherever they are not text the widget itself shows or its window title (`simulation_view._spoken_text`). Each such string is marked as not seen, so `visible_strings` leaves it out, and a test that a user is told something cannot pass on a sentence only a screen reader hears. A button's accessible name, which `_widget_text` used to yield as seen, is now one of them. The strings are read through the accessible interface rather than from `DescribedGraphic` alone, so every route by which Qt writes a name or a description is covered: a name or a description set on the widget, a tool tip, the label a control is named by, the plain form of a rich-text label, and a line edit's placeholder.

The wording test lists each such string after which text it is and the class of the widget that says it, such as "Description of WashInChart: Model outputs — not measurements." (`InterfaceText.spoken_as`, read through `SimulationView.interface_texts`). Without that, a line dropped from a description would still be listed wherever the screen or another kind of widget shows the same words, and the drop would pass unread. `_widget_text` also yields the prefix and suffix drawn in a spin box, such as " ×MAC" beside a MAC target's height and " s" beside its instant, and an empty line edit's placeholder, "Optional". Those were drawn on screen and outside the list too.

The approved list gained 231 strings, each read before it was added: the three graphics' names and description lines, the readouts' and sliders' spoken names with their run, hedge or unit, the plot controls' and selectors' names, the Area border's and corner's names and descriptions, the menus' and choosers' descriptions, the fields' names, the two unit suffixes and the placeholder. It lost 30, which are the buttons' accessible names, each now listed after "Name of QPushButton", "Name of QCheckBox" or "Name of QToolButton". No text on screen or spoken changed. The list is the same when the test runs in DejaVu Sans, the font CI draws in.

**Regression check.** The two first tests fail on the code before the fix (`git stash push src/anesthesia_sim/app/simulation_view.py`, then `pytest tests/integration/test_interface_wording.py::test_a_changed_line_that_only_a_screen_reader_hears_differs_from_the_approved_list tests/integration/simulation_view/test_simulation_view_whole_interface.py::test_what_a_screen_reader_alone_is_told_is_held_but_not_seen`). The first fails with `assert (2 + 0) == 63`, because every approved spoken string is gone. The second fails because the concentration chart's description lines, such as "Line chart.", are not among the strings held. `test_a_line_dropped_from_a_description_differs_where_the_screen_shows_the_same_words` fails on the first version of the fix, which listed each line as bare words, with that version's approved list. Its differences held only the two unit suffixes that version did not yet read, and no line for the dropped "Model outputs — not measurements.", because the screen shows the same words beside the plot.

**Blind review.** Two passes, six findings:

1. Pass 1, should-fix, and pass 2, should-fix, repeated: a button's accessible name was still counted as seen, so the claim that no screen-reader sentence counts as seen was false. Fixed: `_widget_text` no longer yields it, and `_spoken_text` yields it as not seen.
2. Pass 1, should-fix, and pass 2, should-fix, repeated: a line dropped from a description passed where the screen or another widget said the same words, as the wash-in plot's "Model outputs — not measurements." and both charts' "Line chart." do. Fixed by listing each spoken line after its text and widget class, with the new test above.
3. Pass 2, should-fix: the unit suffixes of the mark editor's fields were drawn and outside the list. Fixed: `_widget_text` yields a spin box's prefix and suffix and an empty field's placeholder.
4. Pass 1, optional: `test_the_interface_never_predicts_a_time_to_wake_up` read the band's "population" and "±1 SD" from every string, so the chart's description alone could satisfy it. Fixed: it reads them from the visible strings.
5. Pass 1, optional: the concentration chart's description gives the MAC-awake band without the legend's "population, read against vessel-rich group trace". Filed as `PL-596J`, because the safety standard reaches it.

**Documents checked.** `docs/INTERFACE.md` gains a paragraph after `PL-9XGQ`'s that says what the wording test holds a screen reader's text to. `docs/ARCHITECTURE.md`'s line on the wording test and that test's module docstring say it reads what a screen reader is told, and how each such line is listed. `docs/maintainer.md` § on wording asks and `.claude/skills/pull-request/SKILL.md` § on `bin/docket arm` are still true, since the docstring's list of changes that wait for the owner applies to the new strings unchanged. `docs/VERIFICATION.md` does not describe the wording test.
