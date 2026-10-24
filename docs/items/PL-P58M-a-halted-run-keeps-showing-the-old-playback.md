---
id: PL-P58M
title: A halted run keeps showing the old playback rate on the clock's second line after the playback-rate dropdown changes, because present_halt does not write the readout row and PL-X7D5's guard exempts _readout_row (reproduced offscreen by PL-K88Z's inventory: 5x in the dropdown, 1x real time in the readout)
priority: P2
effort: S
status: ready
classes: defect, ux
feature: one-source-of-truth
touches: src/anesthesia_sim/app/run_view.py, tests/integration/test_simulation_view.py
added: 2026-10-19
payoff: a halted run states one playback rate, the one the learner just chose
verify: grep -q 'def test_a_halted_run_shows_the_new_playback_rate' tests/integration/test_simulation_view.py
---

**Problem.** A halted run keeps showing the old playback rate on the clock's second line after the playback-rate dropdown changes, because present_halt does not write the readout row and PL-X7D5's guard exempts _readout_row (reproduced offscreen by PL-K88Z's inventory: 5x in the dropdown, 1x real time in the readout)

**Why it matters.** After the learner changes the playback rate on a halted run, the dropdown shows the new rate and the clock's second line still shows the old one. The screen then states two playback rates at once. A learner timing an event against the clock can misjudge how fast simulated time is passing. `PL-X7D5` built a guard so that a halt restates every widget, and `FRAME_WIDGETS` in `tests/integration/test_simulation_view.py` exempts `_readout_row` from it.

**Done when.** A change of playback rate on a halted run rewrites the readout row's playback line. `_readout_row` is no longer exempt in `FRAME_WIDGETS`, or the exemption names why the guard cannot reach it and another test covers it. A test named `test_a_halted_run_shows_the_new_playback_rate` in `tests/integration/test_simulation_view.py` fails on today's code and passes after the fix.

**Checked 2026-10-24.** Nothing under `src/` or `tests/` has changed since `PL-K88Z` reproduced this offscreen on 2026-10-23 (5x in the dropdown, 1x real time in the readout).
