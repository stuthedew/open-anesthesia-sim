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

**Why it matters - this is the safety half of bookmarks.** The overshoot is
silent and speed-dependent: the same bookmark halts at a different
concentration depending on how fast the learner was running, so the displayed
halt value is not the value that was asked for. That is a
presentation-correctness failure of the kind `CLAUDE.md` treats as
safety-critical, and it also breaks reproducibility of any branch taken from
that bookmark, because two branches nominally taken "at 0.8 MAC" would start
from different states.

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
an unreachable threshold ends in a distinct, visible not-reached outcome; and
`docs/MODEL.md` states the halt semantics.
