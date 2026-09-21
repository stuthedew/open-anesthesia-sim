---
id: PL-C3GS
title: The agent-accounting and control-change panels stack unattributed in the shared sidebar column once a branch is drawn, so 'What was changed during this run' names no run and a setting change reads as the other run's
status: untriaged
feature: two-run-attribution
added: 2026-09-21
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
about by a channel that does not depend on stacking order, held by a test in
`tests/integration/test_simulation_view.py`.
