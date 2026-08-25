---
id: PL-PFM1
title: Detect threshold-bookmark crossings inside the advance loop, not at frame boundaries
status: dropped
feature: scenario-branching
added: 2026-08-25
closed: 2026-08-25
reason: aspirational rather than actionable; there is no bookmark to detect a crossing for, so it was promoted to ROADMAP.md planned milestone 26 as a required property of bookmarks
---

**Problem.** A threshold bookmark ("stop when VRG reaches 0.8 MAC") is only
correct if the crossing is tested on every simulation step. Testing it once
per rendered frame overshoots by the whole frame's worth of simulated time,
and the faster the playback multiplier, the worse the overshoot.

**Why it matters.** The overshoot is silent and speed-dependent: the same
bookmark stops at a different concentration depending on how fast the user
was running, and the displayed halt value would not be the value asked for.
That is a presentation-correctness failure of the kind `CLAUDE.md` treats as
safety-critical, and it also breaks reproducibility of any branch taken from
that bookmark. Interacts directly with PL-009 (playback speed multiplier),
which is what makes many steps per frame the normal case.

**Where.** `app/controller.py` (`advance`), and the crossing predicate in
`core/` alongside the bookmark definition.

**Done when.** A threshold bookmark halts at the same simulated time and the
same concentration at every playback speed, with a test that runs one
scenario at several multipliers and asserts identical halt state.
