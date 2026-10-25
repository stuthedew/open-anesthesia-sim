---
id: PL-XV0D
title: A run's halt record, bookmark_halt, is filtered by instant when a mark is removed rather than re-derived from the current marks as the standings are since PL-1ZQ4, so a branch reset after a mark was removed and re-added names the removed mark and its old label, and a trunk halted on a mark loses "stopped on your mark" from its Branch here button once the same mark is removed and added back, although its row still reads passed
priority: P3
effort: S
status: ready
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py
added: 2026-10-25
payoff: the Branch here button and the halt record agree with the marks panel after a mark is removed and added back
verify: grep -q 'def test_the_halt_record_follows_the_current_marks_after_a_mark_is_removed_and_added_back' tests/integration/test_controller.py
---

**Problem.** `_forget_unmarked` keeps a halt's marks by instant alone (`src/anesthesia_sim/app/controller.py`). `_stand_on` restores a branch's halt from the frozen crossing at reset (`controller.py`). So after a learner removes a mark on a branch, adds an equal mark with a new label, and resets, `bookmark_halt` holds the removed `TimeBookmark` with its old label. That object is not in the run's bookmark set. On the trunk, removing and re-adding the mark it halted on clears `bookmark_halt`. The Branch here button then drops "stopped on your mark", while the row reads passed, because the standings re-ask the step with the current marks (`controller.py`).

**Why it matters.** Today the interface reads only whether `bookmark_halt` is set, so the stale label is not on screen. The trunk's label change is on screen, and it disagrees with the row beside it. Any fix for 775-M that names the halting mark would show the removed mark's label. Deriving the halt record from the step and the current marks, as `PL-1ZQ4` did for the standings, would remove both.

**Done when.** `bookmark_halt` is derived from the step and the current marks, as the standings are, so after a mark is removed and an equal one added, a branch reset names the current mark and the trunk keeps "stopped on your mark". `tests/integration/test_controller.py` has `test_the_halt_record_follows_the_current_marks_after_a_mark_is_removed_and_added_back`.

**Found by.** `PL-TBQS` reviewer replay on #805, findings 805 r02 F3 and 805 r05 F2 (their standing-flip half is fixed by `PL-1ZQ4`), checked against main on 2026-10-25. Reproduced with `scratchpad/r/scripts/d_805.py` and `d_805_trunk.py`: after reset the branch's halt named 'orig' while the panel listed 'again', and the trunk's `here_fork_point.stopped_on_mark` went from True to False on re-adding the mark.
