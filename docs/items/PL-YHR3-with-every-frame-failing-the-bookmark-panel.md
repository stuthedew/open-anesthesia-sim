---
id: PL-YHR3
title: With every frame failing, the bookmark panel keeps the last frame's standings: a mark the failed run will never reach goes on reading '10m - later' where a drawn frame of the same failed run reads '10m - later · not reached before the simulation error', because _halt_every_run restates the fork panel but not the bookmark panel (found building PL-X7D5)
priority: P2
effort: S
status: done
classes: defect, ux
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_simulation_view.py, docs/ARCHITECTURE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed at filing, 2026-10-17
added: 2026-10-17
closed: 2026-10-19
pr: 1670
payoff: a paused run whose frames fail stops showing the last frame's bookmark standings, so a mark the failed run will never reach no longer reads as still to come
verify: grep -q 'def test_a_failing_frame_withdraws_the_last_frames_bookmark_standings' tests/integration/test_simulation_view.py
recurrences: 2026-10-17 PL-5JTH
---

**Problem.** With every frame failing, the bookmark panel keeps the last frame's standings: a mark the failed run will never reach goes on reading '10m - later' where a drawn frame of the same failed run reads '10m - later · not reached before the simulation error', because _halt_every_run restates the fork panel but not the bookmark panel (found building PL-X7D5)

**Reproduced 2026-10-17**, offscreen, while building `PL-X7D5`'s second pull
request, with a scratch script: a trunk advanced 100 steps of 0.1 s, a fresh
gas flow change, paused, a time bookmark added at 600 s, then every frame made
to fail by replacing `simulation_view.assemble_chart_frame` with one that
raises. After the failing `present(False)` the run reads "Stopped -
simulation error" and the bookmark row still reads "10m – later". With the
patch undone, the next drawn frame of the same failed run reads "10m – later
· not reached before the simulation error".

**The mechanism.** `SimulationView._refresh_bookmarks` is called only from
`_refresh_view`, from the frame's snapshots, and `_halt_every_run` restates
each `RunView` and, since `PL-MMNX`, the fork panel, but not the bookmark
panel. The standings need no snapshot: `SimulationController._bookmark_standings`
builds them from the reached instants, the reached crossings, the clock and
the failure, none of them a compartment value, and `BookmarkSet.standings`
reads no trajectory.

**Why it matters.** A row reading "later" tells a learner to wait for a mark
the failed run will never reach, which is the stale-state presentation this
feature removes. **Reachable only through a render-path raise**, which no
supported setting produces today, so `defect`/`ux` at `P2` with its siblings.

**Done when.** `SimulationController` hands out each run's bookmarks and
standings without building a snapshot, and `_halt_every_run` restates the
bookmark panel from them after every run's `present_halt`, guarded as
`_restate_fork_panel` is, so the restatement cannot raise out of the halt
path. A regression test in `tests/integration/test_simulation_view.py`,
`test_a_failing_frame_withdraws_the_last_frames_bookmark_standings`, repeats
the reproduction above and asserts the row reads the failed run's standing.

**Fixed 2026-10-19.** `SimulationController` now exposes `bookmarks` and
`bookmark_standings()`, which build no compartment value.
`SimulationView._restate_bookmark_panel` reads them on a halt, after every
run's `present_halt`, and draws the panel through the same `_refresh_bookmarks`
that a drawn frame uses. If the restatement itself raises, the panel hides
both listings (`BookmarksPanel.withdraw`) rather than keep the last frame's
rows. The editor dialog's lists are left as they are, because a removal
selects a mark by its row there.

**The regression test fails on the code before the fix.** Run against the
unfixed tree with
`QT_QPA_PLATFORM=offscreen uv run pytest -q -p no:randomly tests/integration/test_simulation_view.py -k withdraws_the_last_frames_bookmark`,
it failed with `AssertionError: assert False` where
`'10m – check'.endswith(' · not reached before the simulation error')`: after
the failing frame, the row still listed the mark as to come. The guard's test,
`test_a_bookmark_panel_that_cannot_be_restated_on_a_halt_lists_no_standing`,
needs the new `bookmark_standings` method, so before the fix it fails at
collection of that attribute (`AttributeError`). The first test is the variant
that does not need the new interface.
