---
id: PL-NKFD
title: The charts redraw on a 0.2 s render tick while a dial is held, twice the 0.1 s that Nielsen Norman Group gives as the limit for a user to feel they are directly manipulating the display; measure the frame cost and whether a 0.1 s tick fits it
status: done
added: 2026-11-22
closed: 2026-11-23
pr: 2264
filed-pr: 2257
tests: tests/integration/simulation_view/test_simulation_view_controls.py::test_a_burst_of_wheel_events_draws_one_frame_at_once_and_the_rest_within_a_tenth_of_a_second, tests/integration/simulation_view/test_simulation_view_controls.py::test_a_render_tick_that_draws_a_burst_s_owed_frame_ends_the_burst, tests/integration/simulation_view/test_simulation_view_loops.py::test_a_dragged_slider_draws_its_first_preview_at_once_and_its_moves_within_a_tenth_of_a_second
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
counting render ticks (`INPUT_FRAME_INTERVAL_S`, `SimulationView.present_input`,
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

- `test_a_burst_of_wheel_events_draws_one_frame_at_once_and_the_rest_within_a_tenth_of_a_second`
  replaces the burst test of `PL-2WVC`. It also pins the timer's interval at
  100 ms, Nielsen Norman Group's limit, and checks that an interval that ends
  with nothing owed ends the burst.
- `test_a_render_tick_that_draws_a_burst_s_owed_frame_ends_the_burst` checks
  that the tick and the end of the 0.1 s never both draw one owed frame.
- `test_a_dragged_slider_draws_its_first_preview_at_once_and_its_moves_within_a_tenth_of_a_second`
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
tests/integration/simulation_view/test_simulation_view_loops.py::test_a_dragged_slider_draws_its_first_preview_at_once_and_its_moves_within_a_tenth_of_a_second`.

**Not measured:** the frame cost on the owner's Mac or in CI. The container
draws in software, so its figures are an upper bound for a machine with a
graphics card, and the design does not depend on them: the render tick
keeps its old cost, and the input frames are bounded by the timer.

**Docs checked:** `docs/INTERFACE.md` (the drag and dial-input paragraph),
`docs/ARCHITECTURE.md` (the halt paragraph that said a dragged dial leaves
the charts to the render tick), `docs/VERIFICATION.md` and `docs/MODEL.md`
(no statement about frame timing).
