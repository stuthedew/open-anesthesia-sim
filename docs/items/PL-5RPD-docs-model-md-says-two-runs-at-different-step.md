---
id: PL-5RPD
title: docs/MODEL.md says two runs at different step sizes are two roundings of the same solution, but a step holds each setting for its whole length, so a control change lands at a different instant on each step grid and two runs with any setting change follow different trajectories by more than rounding
priority: P1
effort: S
status: done
classes: docs, science
feature: replay-findings
touches: docs/MODEL.md
added: 2026-10-25
closed: 2026-10-26
pr: 1864
payoff: a reader comparing two runs at different steps does not dismiss a real difference in a control change's timing as rounding noise
verify: grep -qF 'Between setting changes, two runs at different' docs/MODEL.md
---

**Problem.** The bullet "A different step size" (`docs/MODEL.md` § "The reproducibility guarantee") says that what separates two runs at different steps is floating-point accumulation. That holds only while every setting stays fixed. A control change takes effect at the next step boundary, which falls at a different time on each grid. The playback paragraph just above it still calls a resized step "a second numerical solution", and the comment above `MAXIMUM_SIMULATION_STEP_S` in `core/simulation_step.py` describes the per-step control delay.

**Why it matters.** A reader comparing two runs could dismiss a real difference as rounding noise. The bullet should say that the equivalence holds between setting changes, and that a change's timing moves with the step.

**Done when.** The bullet "A different step size" in `docs/MODEL.md` § "The reproducibility guarantee" says that two runs at different steps differ only by rounding between setting changes, and that a change's timing moves with the step grid.

**Found by.** `PL-TBQS` reviewer replay on #376, finding r02 F2. Checked against main on 2026-10-25: the bullet is unchanged.
