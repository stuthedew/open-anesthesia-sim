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

**A candidate fix, not yet verified:** when a run that was running before a
tick is not running after it, `step_tick` asks for a coalesced frame
(`presentation_requested(True)`), so `render_tick` owes and draws one; and a
regression test driving the real timers rather than `present(False)`.
