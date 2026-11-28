---
id: PL-GWSY
title: A chart or schematic top chosen while the preferences cannot be saved is said to be unsaved only in the agent cost View, so a Workspace without that View gives no sign that the top will reset at the next launch
priority: P3
effort: S
status: done
classes: defect
feature: chart-readout
touches: src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/view_contract.py, src/anesthesia_sim/app/view_registry.py, tests/unit/test_dashboard_frame.py, tests/integration/test_view_contract.py, tests/integration/test_layout_adapter.py, docs/INTERFACE.md
deferred-from: v0.7.0 - new: PL-7LZ7 made the axis top a saved preference on 2026-11-28; not safety or science, and no user sees a wrong value from it, since the axis and its control show the top in force (triage 2026-11-28)
added: 2026-11-28
closed: 2026-11-28
pr: 2368
filed-pr: 2341
payoff: a user who picks an axis top while preferences cannot be saved is told it will not be kept, whichever Views are open
tests: tests/unit/test_dashboard_frame.py::test_the_line_under_an_axis_top_control_names_the_first_problem_that_holds, tests/integration/test_view_contract.py::test_a_file_the_launch_could_not_use_is_named_on_every_chart_and_schematic, tests/integration/test_view_contract.py::test_a_top_that_could_not_be_saved_is_named_on_every_chart_and_schematic
---

**Problem.** A chart or schematic top chosen while the preferences cannot be saved is said to be unsaved only in the agent cost View, so a Workspace without that View gives no sign that the top will reset at the next launch

**Found on 2026-11-28** while building `PL-7LZ7` (one axis top for every chart and schematic). The axis top is now a preference, saved in `preferences.json`. When a save fails, or saving is off because the file was written by a newer build or could not be checked, `SimulationView._change_preferences` puts the reason in the preferences notice. Only `AgentCostView` shows that notice. A reader who picks a top in a Workspace with no agent cost View is not told that the top lasts only until the application closes.

**Why it matters.** It is not a wrong value: the axis and the control show the top in force. It is a setting that silently does not persist, which `app/preferences.py`'s rule that no problem with the file passes without a notice is meant to prevent.

**What a fix needs to decide.** Where a reader who is not looking at the agent cost View learns that preferences are not being saved. One candidate is the same line under each "Axis top" control that names a refused saved top (`preferences.chart_ceiling_notice`). The other is one application-wide notice. The wording follows the sources `PL-VT87` recorded.

**Generator check.** A one-off: the first preference set outside the agent cost View.

**Reproduced 2026-11-28.** `preferences_notice` is built only in `AgentCostView` in `src/anesthesia_sim/app/views.py`, and `SimulationView._change_preferences` in `src/anesthesia_sim/app/simulation_view.py` writes the unsaved-change reason into it (`unsaved_preferences_notice`).

**Done when.** A test that makes saving fail, then picks an axis top in a Workspace that shows no agent cost View, finds a notice in view saying that the top lasts only until the application closes. Where that notice goes is a placement choice, so the session that builds it decides it from a cited source, as rule 14 of `.claude/rules/instruction-writing.md` says, and records the source here.

**Fixed 2026-11-28.** Every concentration chart and compartment schematic
says under its "Axis top" control when the top in force will not be the one
the next launch opens at: "The application could not save this axis top, so it
lasts only until the application closes. The Agent cost View says why." That
happens when saving is off for the session or a save fails. Choosing the top
the next launch opens at again clears the line, and so does a later save that
succeeds, because it writes the top in force. When the launch could not use
the preferences file at all, because a newer version wrote it or it could not
be read or used, the line says from launch: "The application could not use
your preferences file, so any axis top saved in it is not in use. The Agent
cost View says why." A refused saved top keeps its own line, which names the
top and says what to do, and which comes first.

`SimulationView` keeps the top that the next launch opens at, with whether the
file holds no refused top, in `_kept_chart_ceiling`: the one loaded, then the
one last saved. `_preferences_in_force` compares the top in force with it on
every tick, and passes the result to every View as
`PreferencesInForce.chart_ceiling_unsaved`. It passes whether the launch
could not use the file as `PreferencesInForce.preferences_file_unused`, which
is true when there is a store and the load turned saving off.
`dashboard_frame.chart_ceiling_line` writes the line, and
`views._show_ceiling_notice` shows it in both Views. The unsaved line points
at the agent cost View's notice, so it is not shown while there is no notice.
That happens only for a dashboard that a test builds with no store, which is
how the existing tests that pick a top see no line. The View's title is
`dashboard_frame.AGENT_COST_VIEW_TITLE`, which the View chooser and both lines
read.

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

**Regression check.** Run with the source tree of the code before the fix
first on `PYTHONPATH` (`git archive origin/main src`, main at `ca539204`):
`test_a_file_the_launch_could_not_use_is_named_on_every_chart_and_schematic`
fails at launch with `assert True is ('The application could not use your
preferences file, ...' is None)`, because no line is shown, and
`test_a_top_that_could_not_be_saved_is_named_on_every_chart_and_schematic`
fails at the first pick with the same assertion for the unsaved line. Against
the first version of this fix (`b8f21e12`, before its blind review), the
first test fails at launch the same way, and the second fails when the kept
top is picked again, with `assert False is (None is None)`, because that
version still showed the line. The unit test of `chart_ceiling_line` cannot be
collected against either, because neither has that function, and the two
integration tests cover the same three lines through the interface.

**Blind review, 2026-11-28.** Two passes. Pass 1 found three optional
faults, all fixed: re-picking the top the file holds still said it could not
be saved; a file the launch could not use gave no line until a pick; and the
line typed the View's title by hand, a second copy of the View chooser's.
Pass 2 found the first two again (optional, fixed) and one should-fix: on the
compartment schematic the line sits in the part that scrolls, while the
control is pinned above it, so a reader scrolled down sees no line. The
refused-top line has the same fault since `PL-7LZ7`, and moving the line
changes the Area's least height, so it is filed as `PL-B3M6`.

**Docs checked at close-out.** `docs/INTERFACE.md` § "The chart's fixed MAC
axis" (a paragraph on both lines, when each shows and its source, and the note
for developers names the tests, the fields and the function),
`docs/MODEL.md` (no mention of the axis top's saving), `docs/VERIFICATION.md`
(none), `docs/PARAMETERS.md` (none), `README.md` (none), and the docstrings of
`chart_ceiling_line`, `PreferencesInForce`, `SimulationView._change_preferences`,
`SimulationView._preferences_in_force` and the two Views' `refresh`.
