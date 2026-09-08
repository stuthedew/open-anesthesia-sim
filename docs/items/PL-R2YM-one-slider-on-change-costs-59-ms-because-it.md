---
id: PL-R2YM
title: One slider on_change costs 59 ms because it triggers a whole-page update: a drag emitting 30 events a second would need 1.8 s of event-loop time per second
priority: P2
effort: S
status: done
classes: perf, ux
feature: vaporizer-controls
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py
added: 2026-09-08
closed: 2026-09-08
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_a_dragged_slider_leaves_its_frame_to_the_render_tick' tests/unit/test_simulation_view.py
---

**Problem.** Every parameter slider is wired `on_change=` rather than
`on_change_end=`, so Flet raises a handler per pointer movement during a drag.
Each handler runs `_apply_setting`, which ends in `_refresh_and_render` and so
in a whole-page `page.update()` — the walk `PL-YSZN` measures at 20-52 ms on a
saturated chart, paid in full for a frame in which no trace moved. Applying
the setting itself is microseconds; the redraw is the whole bill.

Measured 2026-09-08 on the harness `PL-YSZN` describes, chart saturated at
300x: 59.1 ms per `on_change` (min 54.0, max 77.5) in one run and 28.5 ms in a
quieter one on the same container. At the lower figure a drag emitting 30
events a second needs 0.9 s of event-loop time per second; at the higher, 1.8 s.
Either way the loop cannot service the drag, and it is doing this on top of the
5 Hz render loop and the simulation burst.

Flet dispatches a sync handler inline on the same event loop the run timers
use, so this is also what delays the *simulation*: `PL-SQJ1` records the rate
shortfall that follows.

**Why it matters.** It is the interaction path — the thing a reader is
touching when they call the interface laggy — and it is the one place where
the whole-page cost is paid for a page that did not change. `PL-027` predicted
exactly this class of unknown ("whether Flet's diff treats a same-value write
as a no-op, and whether a write landing mid-drag snaps the thumb, was not
verified") and left it for a live client; the diff does not treat it as a
no-op, and no live client is needed to show that.

**Care required.** The write-back this would defer is a presentation-correctness
fix (`PL-018`): `_refresh_view` restores every slider from the snapshot so a
*refused* setting cannot leave a control showing a dial position the simulation
is not running at. Anything that stops rendering on each `on_change` has to keep
rendering immediately on a refusal, and has to account for a paused run, where
`_run_render_timer` takes no frames at all and a deferred refresh would never
arrive.

**First step.** Decide between narrowing the redraw to the controls a setting
change can reach, deferring the redraw to the next render tick with an
immediate render on refusal, and moving the sliders to `on_change_end`. Then
measure the drag cost again on the same harness.

**Resolved: the slider's frame is coalesced onto the render tick; everything
else still draws its own** (project owner, 2026-09-08, approving the deferral
route over narrowing the redraw and over `on_change_end`).

**Deferring only `page.update()`, not `_refresh_view`.** The route as proposed
was to defer the redraw whole. Splitting it is strictly better and gives up
nothing: `_refresh_view` costs 3-4 ms against `page.update()`'s 23-59 ms, so
running it on every event keeps 85% of the saving — and it is what preserves
`PL-018`'s property, that the control objects agree with the snapshot the
moment a setting is applied. Every existing test passed unchanged under this
variant and five would have failed under the other, which is the suite saying
the invariant was deliberate rather than incidental.

**Two carve-outs, and they are the same fault in opposite directions.** A
refusal draws its own frame, because it is the one case where the dial on
screen and the simulation disagree — the reader dragged it somewhere the core
would not go — so a tick of delay leaves a control stating a setting the run
is not using. And the call that *clears* a refusal draws too, because a notice
left up after it stopped being true misstates the run the same way. An
accepted setting with no notice on either side of it has nothing on screen to
correct.

**The render tick now fires while the run is stopped**, whenever a change is
owed a frame. Without that the bound would not hold on the pause-change-resume
route `app/playback.py` documents as the way to time a control change exactly:
paused there is no run to draw, but there is still a dial moving.

Measured on the harness `PL-YSZN` describes, saturated chart at 300x, one
slider `on_change`:

| | Per event | A 30-event/s drag needs |
| --- | ---: | ---: |
| As found | 59.1 ms | 1.8 s of loop time per second |
| After `PL-KP7H` (tooltips off while playing) | 23.3 ms | 0.7 s |
| After this | 3.4 ms | 0.1 s |

**What it costs.** A change now reaches the client up to `RENDER_INTERVAL_S`
later — 200 ms, the cadence every other readout on the dashboard already moves
at. That is a bound rather than a regression: at 30 events a second the old
path asked for more loop time than a second contains, so the readouts arrived
*later* than a tick and unpredictably. The immediacy was claimed rather than
achieved.

**What it hands on.** `PL-027` keeps the half that needs a live client: whether
a same-value write landing mid-drag snaps the thumb. Its other half — whether
the write-back costs anything — is answered, and the answer was that the cost
was never the write.
