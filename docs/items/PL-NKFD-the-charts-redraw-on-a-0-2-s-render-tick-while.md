---
id: PL-NKFD
title: The charts redraw on a 0.2 s render tick while a dial is held, twice the 0.1 s that Nielsen Norman Group gives as the limit for a user to feel they are directly manipulating the display; measure the frame cost and whether a 0.1 s tick fits it
status: done
milestone: v0.6.22
added: 2026-11-22
closed: 2026-11-23
pr: 2264
filed-pr: 2257
tests: tests/integration/simulation_view/test_simulation_view_controls.py::test_a_burst_of_wheel_events_draws_one_frame_at_once_and_the_rest_when_the_wait_ends, tests/integration/simulation_view/test_simulation_view_controls.py::test_a_render_tick_that_draws_a_burst_s_owed_frame_ends_the_burst, tests/integration/simulation_view/test_simulation_view_loops.py::test_a_dragged_slider_draws_its_first_preview_at_once_and_its_moves_when_the_wait_ends, tests/unit/test_dashboard_frame.py::test_two_input_frames_start_the_interval_or_twice_the_cost_apart
---

**Problem.** The charts redraw on a 0.2 s render tick while a dial is held, twice the 0.1 s that Nielsen Norman Group gives as the limit for a user to feel they are directly manipulating the display; measure the frame cost and whether a 0.1 s tick fits it

**Found 2026-11-22** while researching the frame timing for `PL-2WVC` (a dial
input's frame drawn at once). `RENDER_INTERVAL_S` in `app/dashboard_frame.py`
is 0.2 s. Nielsen Norman Group, "Response Times: The 3 Important Limits"
(https://www.nngroup.com/articles/response-times-3-important-limits/, read in
full on 2026-11-22), gives "0.1 second: Limit for users feeling that they are
directly manipulating objects in the UI". While a dial is held, the readouts
follow the dial at once but the charts follow it only every 0.2 s.

**Done when.** The cost of one full frame is measured on the reference
machine and in CI, and the render tick is set to 0.1 s if a frame fits in
it, or the item records why it cannot.

**Measured 2026-11-22** in the cloud container (offscreen Qt, software drawing),
with a script kept outside the repository: the dashboard as `open_dashboard` builds it, in
a 1920 x 1080 window, one `present(False)` plus a repaint per step, 40 frames
each.

| Run length | Median | 95th percentile | Worst |
| --- | --- | --- | --- |
| 60 s | 23.1 ms | 25.2 ms | 33.1 ms |
| 600 s | 34.7 ms | 49.7 ms | 76.2 ms |
| 1800 s | 44.5 ms | 64.2 ms | 87.6 ms |
| 3600 s | 39.8 ms | 61.7 ms | 63.5 ms |

One simulation step costs 0.07 ms, so even 300x playback (30 steps a tick)
adds about 2 ms. The frame is the cost.

**Design chosen.** Nielsen Norman Group's 0.1 s limit is for *direct
manipulation*; a chart that follows a running run with no hand on a dial is
not being manipulated. A fixed 0.1 s render tick would double the drawing
load all the time a run plays, to roughly a quarter to a half of one core
here, to meet a limit that applies only while a dial moves. So the tick stays
at 0.2 s, and a dial input is drawn at once, or 0.1 s after the last input's
frame when it follows one more closely than that, instead of waiting for the
tick: the throttle that `PL-2WVC` built, with its wait set to the
manipulation limit and measured by a 0.1 s single-shot timer rather than by
counting render ticks (`INPUT_FRAME_INTERVAL_MS`, `SimulationView.present_input`,
`input_frame_due`). A held thumb's preview moves now go through the same
throttle, so the first move draws at once and the rest within 0.1 s, where
they had waited for the render tick since `PL-R2YM`. The cost during a burst
is at most ten input frames and five tick frames a second, about 15 x 40 ms,
and only while a dial moves. Qt's QTimer
emits an overrun timeout once and does not queue missed ones
(https://doc.qt.io/qt-6/qtimer.html, read 2026-11-22), so a frame slower than
the wait cannot build a backlog. MDN's requestAnimationFrame page (read
2026-11-22) describes the same one-shot, one-frame-pending pattern browsers
use for animation.

**What changed in the tests.**

- `test_a_burst_of_wheel_events_draws_one_frame_at_once_and_the_rest_when_the_wait_ends`
  replaces the burst test of `PL-2WVC`. It also pins the timer's interval at
  100 ms, Nielsen Norman Group's limit, and checks that an interval that ends
  with nothing owed ends the burst.
- `test_a_render_tick_that_draws_a_burst_s_owed_frame_ends_the_burst` checks
  that the tick and the end of the 0.1 s never both draw one owed frame.
- `test_a_dragged_slider_draws_its_first_preview_at_once_and_its_moves_when_the_wait_ends`
  replaces `test_a_dragged_slider_leaves_its_frame_to_the_render_tick`.
- The two halt tests that drag a dial into a halt in
  `test_simulation_view_run_stops_itself.py` now make the snapshot refuse
  after the press, because the press's preview frame is drawn at once and
  would otherwise halt the run before the release applies the value. What
  they check is unchanged.
- The stale-state walk in `test_view_contract.py` reads a line's position as
  a float. pyqtgraph skips a move to an equal position, so a new line placed
  at 0.0 kept the int 0 it was built with, and the walk reported 0 against
  0.0 for one gridline at one place on screen.

**Before the fix**, on origin/main at 76d01fa9 with the new tests copied in:
the drag test failed with `assert 1 == (1 + 1)` at the press, because the
preview waited for the tick, and the burst test failed with `AttributeError:
'SimulationView' object has no attribute '_input_frame_timer'`. Command:
`QT_QPA_PLATFORM=offscreen PYTHONPATH=src python -m pytest -q
tests/integration/simulation_view/test_simulation_view_loops.py::test_a_dragged_slider_draws_its_first_preview_at_once_and_its_moves_when_the_wait_ends`.

**Not measured:** the frame cost on the owner's Mac or in CI. The container
draws in software, so its figures are an upper bound for a machine with a
graphics card, and the design does not depend on them: the render tick
keeps its old cost, and the input frames are bounded by the timer.

**Docs checked:** `docs/INTERFACE.md` (the drag and dial-input paragraph),
`docs/ARCHITECTURE.md` (the halt paragraph that said a dragged dial leaves
the charts to the render tick), `docs/VERIFICATION.md` and `docs/MODEL.md`
(no statement about frame timing).

**Review fix, 2026-11-23.** Both blind review passes found that the wait was
counted from the end of a frame, so an input reached the charts about 100 ms
plus a frame later, and one pass found that the render tick drew a second
frame a few milliseconds after an input frame during a drag. A frame with a
held thumb's preview on screen, measured the same way, costs more than the
table above:

| Run length | Median | 95th percentile | Worst |
| --- | --- | --- | --- |
| 60 s | 40.0 ms | 56.6 ms | 64.0 ms |
| 600 s | 61.5 ms | 74.6 ms | 106.6 ms |
| 1800 s | 103.0 ms | 142.2 ms | 149.8 ms |
| 3600 s | 104.0 ms | 150.5 ms | 178.2 ms |

So a fixed 100 ms from start to start would keep the interface's thread
drawing all the time during a drag over a long run, and the run's own steps
and the reader's inputs would wait behind it. The wait after an input frame is
now worked out from that frame's measured cost (`input_frame_wait_ms` in
`app/dashboard_frame.py`): the next frame starts 100 ms after this one
started, or twice its cost after, whichever is later. A frame cheaper than
50 ms meets Nielsen Norman Group's limit, and a slower one is followed by an
idle pause as long as itself, which caps drawing at half the thread. A render
tick during a burst is drawn as an input frame, so the wait starts again from
it. The half-thread cap is this project's choice, not a published figure: it
is the load that the 0.2 s tick already put on the thread during a drag over
a long run before this change (about 104 ms of drawing in each 200 ms).

Tests added for the fix: `test_an_input_frame_waits_out_the_interval_or_its_own_cost`,
`test_two_input_frames_start_the_interval_or_twice_the_cost_apart` and
`test_an_input_frame_s_wait_refuses_a_cost_no_clock_can_measure` in
`tests/unit/test_dashboard_frame.py`. Their expected waits are worked out by
hand from the rule.
