---
id: PL-CTD7
title: Detect a bookmark crossing inside the advance loop, with an explicit not-reached outcome
priority: P2
effort: M
status: blocked
blocked-by: PL-LPLD
classes: safety, feature, anticipated
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core/simulation.py, tests/unit, docs/MODEL.md
added: 2026-09-06
---

**Problem.** A threshold bookmark ("stop when the vessel-rich group reaches 0.8
MAC") is only correct if the crossing is tested on every simulation step.
Testing it once per rendered frame overshoots by the whole frame's worth of
simulated time, and the faster the playback multiplier the worse it gets.

**`PL-NBWP` measured that "worse", and the number is larger than this item
assumed** (closed 2026-09-06, pull request 383). A tick advances its whole
burst with nothing between the steps, so the reachable grid is `multiplier x
0.1` s: 0.1 s at 1x, then 0.5, 2, 6 and 30 s. Per-frame detection would
therefore overshoot by up to **30 simulated seconds** at 300x, not by a vague
frame's worth, and `docs/MODEL.md` s "Supported simulation step" now carries
what one grid step of that costs a displayed compartment - percentage points
on an abrupt manoeuvre, against the hundredths the 1x tolerance is stated in.

**Why it matters - this is the safety half of bookmarks.** The overshoot is
silent and speed-dependent: the same bookmark halts at a different
concentration depending on how fast the learner was running, so the displayed
halt value is not the value that was asked for. That is a
presentation-correctness failure of the kind `CLAUDE.md` treats as
safety-critical, and it also breaks reproducibility of any branch taken from
that bookmark, because two branches nominally taken "at 0.8 MAC" would start
from different states.

**The halt must leave the run paused, and that requirement is `PL-NBWP`'s
consequence rather than this item's own.** A halt is detected *inside* the
loop, so it can land on the exact crossing step - finer than the grid any live
control change can reach. What the learner does next cannot: `PL-NBWP`
established that a setting changed while the run is playing first acts at a
tick boundary, so at 300x "halt at 0.8 MAC, then turn the vaporizer off" turns
it off up to 30 simulated seconds after the value the learner was looking at.
The displayed halt would be right and the action taken from it wrong, which is
the same presentation failure one step along. `PL-NBWP` documents the route -
pause, change, resume, because no steps are taken while paused and the setters
apply unconditionally - and a bookmark halt that pauses makes that route
automatic instead of something the learner has to know. So the halt pauses;
resuming is explicit.

**A threshold above a compartment's asymptote is never reached**, so the
outcome set is three-valued rather than two: reached, not reached within the
run-time cap, and still running. "Not reached" must read differently from
"reached" rather than the run stopping silently at the cap.

**Where.** The advance loop in `src/anesthesia_sim/app/controller.py`, and
whatever `core/simulation.py` has to expose for a per-step test that does not
put simulation logic in a UI callback. `docs/MODEL.md` records that a halt is
reported at the first step on which the threshold is crossed, and what that
means for the value displayed.

**Done when.** A crossing is detected on the step that crosses it at every
playback multiplier, asserted by test at 1x and 300x with the same halt state;
the run is left paused at the halt, asserted by test, so a control change made
from it is step-exact rather than landing on the next tick boundary; an
unreachable threshold ends in a distinct, visible not-reached outcome; and
`docs/MODEL.md` states the halt semantics and that a halt lands on an instant
finer than the control grid s "Supported simulation step" publishes.
