---
id: PL-T995
title: A run that stops itself inside RunView.step_tick - a bookmark halt, or arrival at the supported run length - is never redrawn: step_tick requests no frame and render_tick draws only while a run runs or a frame is owed, so the screen keeps saying Running with a live Pause, a clock one step behind, and no Branch here button, until the learner presses something
status: untriaged
added: 2026-10-12
---

**Problem.** A run that stops itself inside RunView.step_tick - a bookmark halt, or arrival at the supported run length - is never redrawn: step_tick requests no frame and render_tick draws only while a run runs or a frame is owed, so the screen keeps saying Running with a live Pause, a clock one step behind, and no Branch here button, until the learner presses something

**Found by the adversarial review of `PL-Y2SL`** (2026-10-12) and confirmed
against the source: `RunView.step_tick` advances the controller and requests
no frame when the run stops itself, and `SimulationView.render_tick` returns
unless a run is running or `_render_pending` is set. Reproduced with the app's
real `QTimer`s, offscreen: the trunk halted on a 60.5 s mark (`is_running`
False, `bookmark_halt` at 60.5 s) while the screen showed the status word
"Running", the clock at 1m0.4s, Pause enabled, no banner, and the "Branch here"
button hidden; it appeared only after a Pause press drew a frame. The same on
`main` before `PL-Y2SL`, with the halt button. The suite cannot see it: every
halt test steps the controller and calls `present(False)` by hand.

**Why it matters.** A screen stating that a stopped run is running, with a
clock behind the run's own, is the stale-state presentation failure
`CLAUDE.md`'s safety-critical standard names, which is why it is filed rather
than fixed in passing. It also hides both halt affordances - the halt's notice
and the button to branch there - which is what a bookmark is for.

**Reproduced again 2026-10-17 at triage**, on this tree (`b9b3c812`), with a
scratch script driving the real `QTimer`s offscreen (`view.start_simulation_timer()`,
Start pressed, `processEvents` until the trunk stopped, then a further second of
render ticks): a trunk paused at 60 s and marked at 60.5 s halted there
(`is_running` False, `bookmark_halt` at 60.5 s) while the screen read status
"Running", clock "1m0.4s", Pause enabled, Start disabled, and the "Branch here"
button hidden; one Pause press drew "Paused" and "Branch here: 1m0.5s, stopped
on your mark". Arrival at the supported run length takes the same path by
source rather than by run - `SimulationController._halt_on_arrival_at_supported_limit`
clears `_is_running` inside `advance` without raising, so `RunView._halt_run`,
the only branch of `step_tick` that emits `presentation_requested`, is not
reached - and was not run to 24 h here. The fault shows only when the last
running run stops itself: `render_tick` draws while `any(run.is_running ...)`,
so a second run still going draws the frame anyway.

**Near neighbour, not a duplicate:** `PL-0LG6` (`add_run` owes no frame) is the
same `render_tick` contract - a frame is drawn only while a run runs or one is
owed - misread at another writer, which is why both sit under
`presentation-safety`.

**Done when.** A run that stops itself inside `RunView.step_tick` - on a mark,
or on arriving at the supported run length - is redrawn by the dashboard's own
timers with no press: within one render tick of the stop its status word, clock,
transport and the "Branch here" offer state the stopped run. A regression test
in `tests/integration/test_simulation_view.py`,
`test_a_run_that_halts_on_a_mark_under_its_own_timers_is_redrawn`, drives the
real step and render timers (or `step_tick` then `render_tick` as the timers
would, never `present(False)` by hand) onto a mark and asserts the status word
is not "Running", Pause is disabled and "Branch here" is shown; the same test or
a sibling covers arrival at the supported run length through `step_tick`.

**A candidate fix, not yet verified:** when a run that was running before a
tick is not running after it, `step_tick` asks for a coalesced frame
(`presentation_requested(True)`), so `render_tick` owes and draws one; and a
regression test driving the real timers rather than `present(False)`.
