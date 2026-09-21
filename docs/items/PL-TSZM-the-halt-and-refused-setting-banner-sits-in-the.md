---
id: PL-TSZM
title: The halt and refused-setting banner sits in the shared notice column with no run attribution, so 'Simulation stopped' and 'the simulation is unchanged and still running its previous setting' read as the dashboard's rather than one run's
priority: P1
effort: S
status: ready
classes: defect, safety, ux
feature: two-run-attribution
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py
added: 2026-09-21
payoff: stops a halt or a refused setting on one run reading as the dashboard's, and stops 'the simulation is unchanged' asserting something false of the run it is not about
verify: grep -q 'def test_the_halt_and_refusal_banners_name_their_run' tests/integration/test_simulation_view.py
---

**Problem.** The halt and refused-setting banner sits in the shared notice column with no run attribution, so 'Simulation stopped' and 'the simulation is unchanged and still running its previous setting' read as the dashboard's rather than one run's

**Found 2026-09-21** while fixing `PL-25DD`, which is the same mechanism one
column over, and verified by reading `SimulationView._place_run` and
`RunView.build_notice`.

**Why it matters.** `_holder(self._notice_column, (run.build_notice(),))` puts
one bare `NoticeLabel` per run into a column the runs share, and
`build_notice` returns `self._notice_text` with nothing naming the run beside
it. All three notices it carries assert something about *a* run and name none:

- `FAILURE_NOTICE_TEMPLATE` - "Simulation stopped - {failure_reason}. The
  values shown are the last completed step ... Reset to start a new run."
- `SUPPORTED_LIMIT_NOTICE_TEMPLATE` - "this run reached the supported run
  length of {run_length}".
- `REFUSED_SETTING_NOTICE_TEMPLATE` - "The simulation is unchanged and still
  running its previous setting."

With two runs drawn, a halt on the branch reads as the dashboard having
stopped, and a refusal on one run states that "the simulation" is still on its
previous setting - which is false of the other run. `docs/MODEL.md`'s hazard
table already carries "reading a run halted by a failure as one the user
paused"; unattributed, the distinction it buys is spent.

**Fix.** `dashboard_frame.compared_run_line(line, frame, run_index)` exists and
does exactly this job for the two chart-column lines (`PL-25DD`, `#823`). The
open question is whether a banner takes the same inline prefix or a run chip,
since it is a coloured block rather than a line of text - that is the design
work, and `.claude/rules/ui-reader.md` governs it.

**Done when.** With two runs drawn, each notice says which run it is about by a
channel that does not depend on stacking order, held by
`test_the_halt_and_refusal_banners_name_their_run` in
`tests/integration/test_simulation_view.py`.
