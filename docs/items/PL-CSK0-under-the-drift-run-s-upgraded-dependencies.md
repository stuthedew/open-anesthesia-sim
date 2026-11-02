---
id: PL-CSK0
title: Under the drift run's upgraded dependencies, test_every_run_state_surface_outside_the_run_view_reads_alike_on_a_drawn_run_and_a_halted_one finds a QWidget that reads differently on a halted dashboard and on the same one drawn; it passes on uv.lock, so either a newer PySide6 exposes a real stale-state surface after a halt or the test reads a property the new Qt changed (drift run 41279184121, 2026-11-01)
priority: P2
effort: M
status: done
classes: defect, test
feature: drift-2026-11-01
milestone: v0.6.14
touches: tests/integration/test_simulation_view.py, src/anesthesia_sim/app/simulation_view.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-01
closed: 2026-11-02
pr: 1937
payoff: the lock can take PySide6 6.12 knowing whether a halted dashboard shows a learner anything stale, instead of the halt-state guard failing unexplained
verify: grep -q 'def test_the_surface_guard_reads_a_scroll_bar_qt_shows_through_its_container_as_the_bar' tests/integration/test_simulation_view.py
not-delegable: the failure has not been reproduced outside CI, so no command on the locked tree fails before the work and passes after it; only a manual run of drift.yml under the upgraded dependencies shows the result
---

**Problem.** Under the drift run's upgraded dependencies, test_every_run_state_surface_outside_the_run_view_reads_alike_on_a_drawn_run_and_a_halted_one finds a QWidget that reads differently on a halted dashboard and on the same one drawn; it passes on uv.lock, so either a newer PySide6 exposes a real stale-state surface after a halt or the test reads a property the new Qt changed (drift run 41279184121, 2026-11-01)

**Evidence.** The test failed in both the `dependencies` and `interpreter`
jobs of drift run 41279184121 with `assert ['QWidget'] == []`. The `order`
job, which runs the suite on `uv.lock` in random order, passed. The run of
2026-10-26 passed all three jobs. Which package moved has not been checked:
the `uv pip list --outdated` step's output is in the job log.

**Checked at triage, 2026-11-01.** Two sentences above are wrong. The `order`
job was skipped in run 41279184121, not passed. The run of 2026-10-26
(40277678595) was the weekly one. It ran only `order` and `doc-quotes`, and it
skipped `dependencies` and `interpreter`. Those two jobs last ran on
2026-10-19, in run 39218413328, a manual run that passed. The `resolved
versions` step of the `dependencies` job shows what moved from `uv.lock`.
PySide6 Essentials and shiboken6 went from 6.11.2 to 6.12.0, and pytest went
from 9.1.1 to 9.2.0. numpy, pydantic, hypothesis, coverage, pluggy and
iniconfig moved by minor or patch releases. The `interpreter` job ran Python
3.15.2.

The failure did not reproduce in this container, on Python 3.14.7 and in file
order. The test passed alone on `uv.lock`. It passed alone with PySide6 6.12.0
and the other locked versions. It passed alone with every upgrade listed above,
and so did the whole of `tests/integration/test_simulation_view.py`, 363 tests.
In the `dependencies` job the test failed on the xdist worker `gw0`, after
tests from other files had run in that worker. So the failure needs something
these runs lacked: a test from another file run earlier in the same process,
or the CI runner's environment. PySide6 6.12.0 alone does not cause it.

**Why it matters.** The test guards a halted run against stale state. After a
halt, every panel outside the runs must read as the same dashboard reads once a
frame draws it. Under the upgraded dependencies the test reports a `QWidget`
that reads differently, and nobody yet knows whether a learner would see
something stale there. Until that is explained, the drift run's `dependencies`
and `interpreter` jobs stay red, and `uv.lock` cannot take PySide6 6.12.0.

It is classed `defect`, not `safety`, for now. The shipped lock still holds
PySide6 6.11.2, on which the test passes. The same test refuses a lock upgrade
that would ship the difference. If the work finds a widget that a learner would
read as stale after a halt, reclass this item `safety` at `P1`.

**Done when.** This brief names the widget that reads differently, the property
that differs and the condition that makes it differ. Then either the halt
restates that widget, or the test stops reading a property that the new Qt
changed and says why. A manual run of `drift.yml` shows the test passing under
the upgraded dependencies.

**Generator check.** Undecided until it is reproduced. If a real widget goes
stale after a halt, it is an instance of `PL-X7D5`'s fact and `PL-J5GC`'s
(what states a run's state, restated on every path that changes it). If the
new Qt only changed a property the test reads, it is a one-off in the test.
Triage on 2026-11-01 could not reproduce it, so the question stays open. The
session that names the widget records the answer here.

**Named 2026-11-02 by drift run 41391573783.** The run was dispatched on this
item's branch, where the guard's failure message prints each differing widget's
state. The `dependencies` job failed on one chain, `QWidget < QScrollArea <
QWidget < QWidget < SimulationView`, and on its third widget only: hidden on the
halted dashboard and shown on the drawn one. A local walk of the same dashboard
names the three widgets. They are `qt_scrollarea_viewport`,
`qt_scrollarea_hcontainer` and `qt_scrollarea_vcontainer`, the private children
that Qt gives every `QScrollArea`. That scroll area is `record_scroll` in
`SimulationView._build_unconditional_region`, the control-change record column
in the band of unconditional values.

- **The widget** is the vertical scroll bar's container in the control-change
  record column.
- **The property** is its hidden flag. Qt shows or hides a scroll bar by showing
  or hiding the bar's container, so the bar's own flag stays false.
- **The condition** is that on the CI runner the record overflowed the band once
  a frame drew the dashboard but not on the halted one, so the bar appeared only
  on the drawn dashboard. The band's height follows the readouts beside it, and
  the drift job is the first to lay them out under PySide6 6.12 on that runner.
  In this container, on x86_64, the record fits in both states, which is why
  three local runs did not reproduce it. Which change in 6.12 moves the heights
  was not established.

**Not stale state, so not reclassed `safety`.** The scroll bar's range already
differs between the two states, and `SURFACE_FRAME_WIDGETS` exempts it as layout.
A learner sees no run value change. Qt shows the bar whenever the record is
taller than the column, so the halted record is never cut off without a bar.

**The fix.** The guard now reads a scroll bar's container as part of the bar.
It skips the two Qt containers in its walk, and it reads a scroll bar's state
with whether the bar is visible within the window. A container that toggles
then shows as a `QScrollBar` difference, under the existing exemption, whose
reason now names both scroll areas. An exemption for the container's own type,
`QWidget`, would have exempted every plain panel on the dashboard.
`test_the_surface_guard_reads_a_scroll_bar_qt_shows_through_its_container_as_the_bar`
makes the record overflow on purpose. It fails without the fix with the CI
failure's own difference, `{'QScrollBar', 'QWidget'}`, and passes with it.

**Closed 2026-11-02 in #1937.** Drift run 41392804086, dispatched on this
branch with the fix, passed all four jobs that had finished when this closed:
`dependencies` (PySide6 6.12.0, pytest 9.2.0), `interpreter` (Python 3.15.2),
`order` and `doc-quotes`. The first run, 41391573783, on the commit before the
fix, failed `dependencies` and `interpreter` on this test alone. In that run's
`interpreter` job, 11768 other tests passed, which is also the first CI proof
for `PL-ZH36`.
