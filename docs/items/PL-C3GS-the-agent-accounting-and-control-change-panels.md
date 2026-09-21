---
id: PL-C3GS
title: The agent-accounting and control-change panels stack unattributed in the shared sidebar column once a branch is drawn, so 'What was changed during this run' names no run and a setting change reads as the other run's
priority: P1
effort: M
status: done
classes: defect, safety, ux
feature: two-run-attribution
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py, docs/MODEL.md
added: 2026-09-21
closed: 2026-09-21
pr: 833
payoff: stops a setting change or a mass-balance status reading as the other run's, which says the trunk received an intervention it never got
verify: grep -q 'def test_the_sidebar_panels_name_the_run_they_record' tests/integration/test_simulation_view.py
recurrences: 2026-09-21 PL-N67T
---

**Problem.** The agent-accounting and control-change panels stack unattributed in the shared sidebar column once a branch is drawn, so 'What was changed during this run' names no run and a setting change reads as the other run's

**Found 2026-09-21** while fixing `PL-25DD`, which is the same mechanism one
column over, and verified by reading `SimulationView._place_run` and
`RunView.build_sidebar_panels`.

**Why it matters.** `_holder(self._sidebar_column, run.build_sidebar_panels())`
puts *two* panels per run into a column the runs share, so a branch makes the
sidebar read: Agent accounting validation, Control changes, Agent accounting
validation, Control changes - four panels, no run named on any of them. The
panels' own words make the misreading concrete rather than theoretical:

- `CONTROL_TIMELINE_CAPTION` is "What was changed during this run, most recent
  first" - "this run" with nothing saying which, over a list of settings and
  the simulated times they took effect.
- `ACCOUNTING_HEADING` is "Agent accounting validation", over a mass-balance
  status and litres of equivalent pure agent.

The control timeline is the worse of the two: comparing two managements of one
patient is the whole point of a branch, so a setting change attributed to the
wrong run says the trunk received an intervention it never got. `build_sidebar_panels`'s
own docstring already states the correct claim - "Both are records of one run"
- which is the thing the screen does not say.

**Fix.** The panels have headings, so the run belongs *in the heading* rather
than as a prefix on a line: `compared_run_line` (`PL-25DD`, `#823`) is the
wrong instrument here, and the right one is probably the heading pair that
`substance_heading` already establishes for the readout section. Confirm
against `.claude/rules/ui-reader.md` before adding any standing text.

**Done when.** With two runs drawn, each sidebar panel says which run it is
about by a channel that does not depend on stacking order, held by
`test_the_sidebar_panels_name_the_run_they_record` in
`tests/integration/test_simulation_view.py`.

**Built 2026-09-21** as `dashboard_frame.compared_panel_heading(heading, run)`,
written by `RunView.set_run_name` into two instance labels the sidebar panels
now hold. Four calls the item left open, and why they went this way:

- **In the heading, as the item proposed**, and the item's own reason holds:
  the panels stack five lines each, so `compared_run_line`'s prefix would say
  the run five times per panel and read as part of each value. A heading exists
  to say what the panel holds, which is where "whose" belongs.
- **The run trails the heading** (`"{heading} — {run}"`) where it leads in
  `COMPARED_RUN_LINE_TEMPLATE`. This is `COMPARED_TRACE_LEGEND_TEMPLATE`'s case
  rather than that one: a panel is found by the kind of record it holds, so the
  kind leads and the run tells two panels of one kind apart, exactly as the
  compartment leads a compared legend entry. The differentiator-first argument
  that puts the run in front of a shared line turns on a wrapped sentence whose
  end a reader must hunt for; a heading is one short bold line. The em dash
  rather than `COMPARTMENT_SUBSTANCE_TEMPLATE`'s colon because "Agent
  accounting validation: Run 2" reads as the validation's *result*, which is
  the word the line directly under it carries (`ACCOUNTING_VALID_TEXT`).
- **One heading per panel, not one heading above both.** A group heading is one
  attribution instead of two, and was refused: `.claude/rules/ui-areas.md` has
  every main element becoming a view in an area a reader can split and
  rearrange, and a heading that sits above two panels stops attributing either
  the moment they are separated. A heading the panel carries survives it. The
  function is kept general over the heading text for the same reason, so the
  next view to earn an area takes the same attribution.
- **Written by `set_run_name` rather than by `refresh`.** What a run is called
  changes when the dashboard's run set changes and at no other time, and
  `_place_run` renames every run the moment a branch is placed - so the
  headings are attributed on the frame the branch appears on, before any chart
  frame is drawn. It also keeps one writer for this run's name, as
  `_apply_agent_color_scheme` is the one writer of its agent colour.

**`docs/MODEL.md` owed the hazard row an edit**, so it joined `touches`. The
row's left column said "concentration" and its mitigation claimed the run is
named "wherever a value is shown" - which the accounting panel's litres of
equivalent pure agent gas made false, and which said nothing at all about the
control-change record, whose misreading is of an *intervention* rather than of
a value. The left column now covers both and the sidebar clause was appended,
rather than a fourth row added: one mechanism - a shared column stacking one
entry per run with no attribution - one mitigation, one place a reviewer looks.

**Found on the way and filed, not fixed** (`feature: sidebar-panel-rebuild`):
`build_sidebar_panels` builds fresh panels on every call and reparents the
run's live labels into them, so a second call strips them out of the sidebar
(`PL-N67T`), which is what makes two assertions in
`test_the_dashboard_fits_its_window_without_a_horizontal_scrollbar` vacuous
(`PL-JS0X`), and `RunView`'s `build_*` methods are split between returning a
stored widget and constructing one with nothing in the names saying which
(`PL-KZR1`). The new integration test holds the live heading labels against
`isVisible` and `isAncestorOf` the sidebar, so that orphaning them is caught
here even while `PL-N67T` is open.
