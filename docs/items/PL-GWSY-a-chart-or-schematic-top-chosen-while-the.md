---
id: PL-GWSY
title: A chart or schematic top chosen while the preferences cannot be saved is said to be unsaved only in the agent cost View, so a Workspace without that View gives no sign that the top will reset at the next launch
priority: P3
effort: S
status: done
classes: defect
feature: chart-readout
touches: src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/preferences.py, src/anesthesia_sim/app/view_contract.py, tests/unit/test_preferences.py, tests/integration/test_view_contract.py, tests/integration/test_layout_adapter.py, docs/INTERFACE.md
deferred-from: v0.7.0 - new: PL-7LZ7 made the axis top a saved preference on 2026-11-28; not safety or science, and no user sees a wrong value from it, since the axis and its control show the top in force (triage 2026-11-28)
added: 2026-11-28
closed: 2026-11-28
pr: 2368
filed-pr: 2341
payoff: a user who picks an axis top while preferences cannot be saved is told it will not be kept, whichever Views are open
tests: tests/unit/test_preferences.py::test_a_picked_top_that_could_not_be_saved_is_named_on_the_charts, tests/integration/test_view_contract.py::test_a_top_that_could_not_be_saved_is_named_on_every_chart_and_schematic
---

**Problem.** A chart or schematic top chosen while the preferences cannot be saved is said to be unsaved only in the agent cost View, so a Workspace without that View gives no sign that the top will reset at the next launch

**Found on 2026-11-28** while building `PL-7LZ7` (one axis top for every chart and schematic). The axis top is now a preference, saved in `preferences.json`. When a save fails, or saving is off because the file was written by a newer build or could not be checked, `SimulationView._change_preferences` puts the reason in the preferences notice. Only `AgentCostView` shows that notice. A reader who picks a top in a Workspace with no agent cost View is not told that the top lasts only until the application closes.

**Why it matters.** It is not a wrong value: the axis and the control show the top in force. It is a setting that silently does not persist, which `app/preferences.py`'s rule that no problem with the file passes without a notice is meant to prevent.

**What a fix needs to decide.** Where a reader who is not looking at the agent cost View learns that preferences are not being saved. One candidate is the same line under each "Axis top" control that names a refused saved top (`preferences.chart_ceiling_notice`). The other is one application-wide notice. The wording follows the sources `PL-VT87` recorded.

**Generator check.** A one-off: the first preference set outside the agent cost View.

**Reproduced 2026-11-28.** `preferences_notice` is built only in `AgentCostView` in `src/anesthesia_sim/app/views.py`, and `SimulationView._change_preferences` in `src/anesthesia_sim/app/simulation_view.py` writes the unsaved-change reason into it (`unsaved_preferences_notice`).

**Done when.** A test that makes saving fail, then picks an axis top in a Workspace that shows no agent cost View, finds a notice in view saying that the top lasts only until the application closes. Where that notice goes is a placement choice, so the session that builds it decides it from a cited source, as rule 14 of `.claude/rules/instruction-writing.md` says, and records the source here.

**Fixed 2026-11-28.** When the reader picks an axis top and the application
cannot save it, because saving is off for the session or the save fails,
every concentration chart and compartment schematic says under its "Axis top"
control: "The application could not save this axis top, so it lasts only until
the application closes. The Agent cost View says why." A later save that
succeeds also writes the top in force, and clears the line. A refused saved
top keeps its own line, which names the top and says what to do.

`SimulationView._change_preferences` records whether the pick was saved in
`_chart_ceiling_unsaved`, and passes it to every View as
`PreferencesInForce.chart_ceiling_unsaved`. `preferences.chart_ceiling_notice`
writes the line, and `views._show_ceiling_notice` shows it in both Views. The
line points at the agent cost View's notice, so it is not shown while there is
no notice. That happens only for a dashboard that a test builds with no
store, which is how the existing tests that pick a top see no line.

**Placement, from a source.** The line goes beside the control the reader
used, not in one application-wide notice. Nielsen Norman Group's
error-message guidelines (https://www.nngroup.com/articles/error-message-guidelines/,
read 2026-11-28): "Display the error message close to the error's source.
Reduce cognitive load by displaying an error indicator adjacent to the
interface where the error occurred." The reason stays in the agent cost View,
because it can hold the whole preferences file's problem and its path, and
Microsoft's Windows error-message guidelines ask to "Avoid putting full file
paths and URLs in the main instruction"
(https://learn.microsoft.com/en-us/windows/win32/uxguide/mess-error, read
2026-11-28). The View is named "Agent cost", as the View chooser names it,
because the Microsoft Writing Style Guide says to "Use sentence-style
capitalization unless you need to match the UI"
(https://learn.microsoft.com/en-us/style-guide/procedures-instructions/formatting-text-in-instructions,
read 2026-11-28). The words "lasts only until the application closes" are
those of `unsaved_preferences_notice`, which the agent cost View already shows.

**Regression check.** Run against the code before the fix (the new tests with
the four source files from the base on `PYTHONPATH`):
`test_a_top_that_could_not_be_saved_is_named_on_every_chart_and_schematic`
fails in both cases with `assert not True` at `assert not
shown.ceiling_notice.isHidden()`, and
`test_a_picked_top_that_could_not_be_saved_is_named_on_the_charts` fails
because `chart_ceiling_notice` takes no `unsaved` argument.

**Docs checked at close-out.** `docs/INTERFACE.md` § "The chart's fixed MAC
axis" (a paragraph on the new line and its source, and the note for
developers names the tests and the field), `docs/MODEL.md` (no mention of the
axis top's saving), `docs/VERIFICATION.md` (none), `docs/PARAMETERS.md`
(none), `README.md` (none), and the docstrings of `chart_ceiling_notice`,
`PreferencesInForce` and `SimulationView._change_preferences`.
