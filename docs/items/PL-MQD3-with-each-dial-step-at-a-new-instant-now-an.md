---
id: PL-MQD3
title: With each dial step at a new instant now an adjustment of its own, an adjustment holds more than one change only where a change follows a branch's opening entry at the fork instant, so the record's interval and settings count, and the two passages of docs/INTERFACE.md that describe them, describe a line a learner almost never sees
priority: P3
effort: S
status: untriaged
classes: cleanup
feature: interface-matches-its-spec
touches: src/anesthesia_sim/app/dashboard_frame.py, docs/INTERFACE.md
added: 2026-11-22
---

**Problem.** With each dial step at a new instant now an adjustment of its own, an adjustment holds more than one change only where a change follows a branch's opening entry at the fork instant, so the record's interval and settings count, and the two passages of docs/INTERFACE.md that describe them, describe a line a learner almost never sees

**Found 2026-11-22** while closing `PL-0T2H` (each dial step at a new instant is an adjustment of its own). `SimulationController._record_in_timeline` in `app/controller.py` now joins a change to the open adjustment only when it is to the same control at the same simulated instant. Two changes to one control at one instant are already one change, because the model uses only the value in place when a step runs (`docs/INTERFACE.md` § "The control-input timeline"). So an adjustment holds two changes only where a branch's opening entry and a change at the fork instant share it. The list's interval form ("10s–1m40s") and its count of settings, in `app/dashboard_frame.py`, and the passages of `docs/INTERFACE.md` that describe them ("A displayed adjustment states the interval it spans and how many settings…", and "One adjustment can hold several changes of one control" under the dashboard's list of what it shows) then serve that edge alone. Decide whether to keep them for it or retire them, and test whichever is kept at that edge.

**Generator check.** One-off. It is the consequence of one decision, `PL-0T2H`'s, not a pattern that files items.
