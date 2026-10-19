---
id: PL-5JTH
title: PL-X7D5's default-include guard compares a RunView's widgets only: the dashboard's own panels a halt must restate - the fork panel (PL-MMNX) and the bookmark panel (PL-YHR3) - are restated by hand in _halt_every_run, so a dashboard panel added later is restated on a halt only if someone remembers to add it there (found closing PL-X7D5)
priority: P1
effort: S
status: done
classes: anticipated
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py, docs/ARCHITECTURE.md
added: 2026-10-17
closed: 2026-10-19
pr: 1675
payoff: a dashboard panel added later cannot keep offering an action over a failed run, because a test fails until the halt path restates it
verify: grep -q 'def test_every_dashboard_panel_is_restated_on_a_halt' tests/integration/test_simulation_view.py
root-cause-of: PL-MMNX, PL-YHR3, PL-F5KT, PL-TLH4
generator: spent - every dashboard panel a halt restates is read from SimulationView.halt_restatements, and test_every_dashboard_control_is_restated_on_a_halt fails on any dashboard control that no RunView, no listed panel and no named exemption holds, so a panel added later fails a test until the halt path reaches it
misread: Which dashboard panels and dialogs state a run's state, and that a halt restates each
recurrences: 2026-10-19 PL-F5KT, 2026-10-19 PL-TLH4
---

**Problem.** PL-X7D5's default-include guard compares a RunView's widgets only: the dashboard's own panels a halt must restate - the fork panel (PL-MMNX) and the bookmark panel (PL-YHR3) - are restated by hand in _halt_every_run, so a dashboard panel added later is restated on a halt only if someone remembers to add it there (found closing PL-X7D5)

**Checked 2026-10-17.** `_halt_every_run` in `app/simulation_view.py` calls
`present_halt` on each `RunView` and then `_restate_fork_panel`. Nothing else is
restated by hand. The default-include guard from `PL-X7D5` compares only a
`RunView`'s widgets, so a dashboard-level panel is outside it.

**Why it matters.** Each panel that `_halt_every_run` misses keeps offering an
action over a run that every other control says has failed. That is the class of
defect the `every-control-restates-the-halt` feature has fixed one panel at a
time (`PL-MMNX` was the latest).

**Done when.** A test fails when a dashboard-level panel that holds a control is
not restated by `_halt_every_run`, in the way `PL-X7D5`'s guard fails for a
`RunView` widget. Either the halt path reaches every such panel through one list,
or the test names each panel it exempts and why.

**Regression check 2026-10-19.** Run with `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/integration/test_simulation_view.py -k <test>` against `src/` as `origin/main` 6fd84bd5 held it. `test_every_dashboard_control_is_restated_on_a_halt`. It needs `halt_restatements`, which the fix added, so on the code before the fix it fails with `AttributeError`. The variant that does not need it: with the bookmark entry deleted from `halt_restatements`, it fails with `these controls are in no RunView and in no panel a halt restates`, first extra item `QComboBox < BookmarkDialog < SimulationView`.
