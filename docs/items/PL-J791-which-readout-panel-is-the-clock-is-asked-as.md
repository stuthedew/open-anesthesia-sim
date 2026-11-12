---
id: PL-J791
title: Which readout panel is the clock is asked as 'quantity is None' in six places under app/, and the clock's playback line is built in three
priority: P2
effort: S
status: ready
classes: defect
feature: one-source-of-truth
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/run_presentation.py, tests/unit/test_dashboard_frame.py
deferred-from: v0.7.0 - captured after the freeze; every displayed value is correct, and one of the six copies came with PL-RF2S after it
added: 2026-11-11
payoff: adding or changing a readout panel cannot put the clock's playback line under the wrong panel
verify: grep -q 'def test_the_clock_panel_is_found_in_one_place' tests/unit/test_dashboard_frame.py
---

**Problem.** Which readout panel is the clock is asked as 'quantity is None' in six places under app/, and the clock's playback line is built in three

**What was found.** The readout row has one panel for the clock, and the code finds it by asking `panel.quantity is None`. That test is written in `app/dashboard_frame.py` (`readouts`, the panel's own row, and twice in `withheld_readouts`), `app/compartment_schematic.py`, `app/run_view.py` and `app/run_presentation.py`. Three of those places then build the clock's second line with `format_playback_rate`: `readouts`, `withheld_readouts` and `run_presentation._at_playback_rate`, which `PL-RF2S` added. The third adversarial review of `PL-RF2S` named the repeat on 2026-11-11.

**Why it matters.** A second panel with no quantity, or a clock that gains one, changes the answer at six places, and nothing fails at the one that is missed.

**Suggested fix.** Give the question one home in `app/dashboard_frame.py`, such as a field on the panel's definition or one function that returns the clock's panel, and one function for the clock's second line. Read both from the six places.

**Done when.** `quantity is None` is asked in one place under `src/anesthesia_sim/app/`, and the clock's playback line is built by one function.

**Reproduced 2026-11-11.** `grep -rn 'quantity is None' src/anesthesia_sim/app/` finds 7 lines, and `format_playback_rate(` is called on 5 lines outside its definition.

**Generator check.** A one-off, filed under the `one-source-of-truth` feature. No head's `misread:` states which readout panel is the clock. `PL-RF2S`, in flight on another branch, changes the same files, so this lands after it.
