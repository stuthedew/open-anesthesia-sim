---
id: PL-96MX
title: The approved on-screen wording test leaves out what a screen reader hears from each chart and diagram, their names and long descriptions, so a change of that wording passes it unread
priority: P3
effort: S
status: done
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_interface_wording.py, tests/integration/approved_interface_strings.json, tests/integration/simulation_view/test_simulation_view_whole_interface.py, docs/INTERFACE.md, docs/ARCHITECTURE.md
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it; each description has its own tests and only the hand check of a later change is missing, so the release waits only on the owner test drive (filed 2026-11-28)
added: 2026-11-28
closed: 2026-11-28
pr: 2360
payoff: a change to what a screen reader hears from a chart, a diagram or a control is read by hand before it merges, as on-screen wording is
tests: tests/integration/test_interface_wording.py::test_a_changed_line_that_only_a_screen_reader_hears_differs_from_the_approved_list, tests/integration/simulation_view/test_simulation_view_whole_interface.py::test_what_a_screen_reader_alone_is_told_is_held_but_not_seen
---

**Problem.** `tests/integration/test_interface_wording.py` holds every string the dashboard shows to a list checked by hand (`approved_interface_strings.json`). It reads them through `SimulationView.interface_strings`, which collects each widget's shown text and a button's accessible name. It does not collect what a screen reader is told by an accessible interface: the name and long description of the concentration chart (`PL-T9RB`), of the wash-in plot and of each run's schematic (`PL-R1M6`), nor a selector's or a label's accessible name. A change to any of those sentences passes the wording test without anyone reading it.

**Why it matters.** Each of these sentences states clinical values in words, such as "Modelled sevoflurane at 10m: Circuit (inspired) 1.45%, 0.81 ×MAC", and says that they are modelled. A screen-reader user reads them in place of the picture, so a wrong label or a dropped "Modelled" there is the same presentation fault as on screen (`CLAUDE.md` § "Safety-critical clinical-output standard"). I suggest P3, because each sentence has its own tests and only the hand check of a later change is missing.

**Approach.** Have `SimulationView.interface_strings` also yield, for each widget, the name and description its accessible interface returns where they differ from the widget's shown text, split into lines as the descriptions are written. Then rerun the wording test, read the new strings and add them to the approved list.

**Done when.** The approved list holds the charts' and the schematic's names and description lines, and a test shows that a changed description line fails the wording test.

**How it was found.** Building `PL-R1M6`, 2026-11-28: its new descriptions passed the wording test without changing the approved list.

**Generator check.** No head states the fact misread here, which is which strings the wording test reads. `SimulationView.interface_strings` collects shown text and a button's accessible name, so a string given only to assistive technology is outside it. This is the first item to name the gap.

**Fixed 2026-11-28.** `SimulationView.interface_strings` now also yields, for each widget, the name and the description that its accessible interface returns, one string for each line, wherever they are not the widget's own shown text or window title (`simulation_view._spoken_text`). Each such string is marked as not seen, so `visible_strings` leaves it out, and a test that a user is told something cannot pass on a sentence only a screen reader hears. The strings are read through the accessible interface rather than from `DescribedGraphic` alone, so every route by which Qt writes a name or a description is covered: a name or a description set on the widget, a tool tip, the label a control is named by, the plain form of a rich-text label, and a line edit's placeholder.

The approved list gained 167 strings and lost none, and each was read before it was added. They are the names and description lines of the concentration chart, the wash-in plot and each schematic; the readouts' spoken names, each with its run and its "modelled" hedge; the selectors', sliders' and plot controls' names with their run, plot or unit; the Area border's and corner's names and descriptions; the menus' descriptions; and the mark name field's placeholder, "Optional". None of them changes clinical meaning, and no text on screen changed. The list is the same when the test runs in DejaVu Sans, the font CI draws in.

**Regression check.** Both new tests fail on the code before the fix (`git stash push src/anesthesia_sim/app/simulation_view.py`, then `pytest tests/integration/test_interface_wording.py::test_a_changed_line_that_only_a_screen_reader_hears_differs_from_the_approved_list tests/integration/simulation_view/test_simulation_view_whole_interface.py::test_what_a_screen_reader_alone_is_told_is_held_but_not_seen`). The first fails with `assert (2 + 0) == 63`, because every approved spoken string is gone. The second fails because the concentration chart's description lines, such as "Line chart.", are not among the strings held.

**Documents checked.** `docs/INTERFACE.md` gains a paragraph after `PL-9XGQ`'s that says what the wording test holds a screen reader's text to. `docs/ARCHITECTURE.md`'s line on the wording test and that test's module docstring say it reads what a screen reader is told. `docs/maintainer.md` § on wording asks and `.claude/skills/pull-request/SKILL.md` § on `bin/docket arm` are still true, since the docstring's list of changes that wait for the owner applies to the new strings unchanged. `docs/VERIFICATION.md` does not describe the wording test.
