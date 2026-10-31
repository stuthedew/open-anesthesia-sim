---
id: PL-F67Q
title: tests/reference/test_coupled_dynamics.py: test_the_disagreement_does_not_shrink_with_the_step drives only three of the five gate trajectories at 0.05 s and 0.025 s, so the 5.89e-14 that EXACT_STEP_ORACLE_TOLERANCE is set against is a maximum over three; the held envelope corner, not driven there, reaches 5.46e-14 for desflurane at 0.025 s, within 8% of it, and three ventilator starts in a row reach 2.46e-14 at 0.1 s against 1.39e-14 for one (measured 2026-10-25 for PL-S86L)
priority: P3
effort: S
status: done
classes: test
feature: numerical-domain
milestone: v0.6.9
touches: tests/reference/test_coupled_dynamics.py, docs/MODEL.md
added: 2026-10-25
closed: 2026-10-25
pr: 1835
payoff: The finer-step gate drives every trajectory the shipped-step gate drives, so the worst residual that the exact step's tolerance is set against is a maximum over all five trajectories rather than three
verify: grep -qF 'all fifteen' tests/reference/test_coupled_dynamics.py && ! grep -qF 'three of the five' docs/MODEL.md
---

**Problem.** tests/reference/test_coupled_dynamics.py: test_the_disagreement_does_not_shrink_with_the_step drives only three of the five gate trajectories at 0.05 s and 0.025 s, so the 5.89e-14 that EXACT_STEP_ORACLE_TOLERANCE is set against is a maximum over three; the held envelope corner, not driven there, reaches 5.46e-14 for desflurane at 0.025 s, within 8% of it, and three ventilator starts in a row reach 2.46e-14 at 0.1 s against 1.39e-14 for one (measured 2026-10-25 for PL-S86L)

**Measured 2026-10-25, on starting it.** `_worst_error_over_phases` on the two trajectories the test leaves out, with the oracle at an eighth of the step under test (`_oracle_step_for`). Each cell gives the worst absolute disagreement, when it was first reached, and in which state:

| Step | Trajectory | Sevoflurane | Isoflurane | Desflurane |
| --- | --- | --- | --- | --- |
| 0.05 s | ordinary use | 5.4678e-15 at 597.25 s, circuit | 2.3349e-15 at 546.75 s, circuit | 1.3677e-14 at 598.40 s, vessel rich |
| 0.05 s | envelope corner, held | 7.3205e-15 at 584.65 s, vessel rich | 1.9679e-14 at 599.95 s, vessel rich | 4.4926e-14 at 600.00 s, muscle |
| 0.025 s | ordinary use | 1.5175e-14 at 600.00 s, vessel rich | 7.9988e-15 at 600.00 s, vessel rich | 9.2287e-15 at 530.75 s, circuit |
| 0.025 s | envelope corner, held | 2.5827e-14 at 496.35 s, circuit | 3.9829e-15 at 593.50 s, vessel rich | 5.4623e-14 at 598.98 s, vessel rich |

None exceeds desflurane's ventilator start at 0.025 s, 5.8870e-14, so the figure the tolerance is set against is the maximum over all five trajectories as well as over three. The six added parametrizations took 1.2 to 1.4 s each at 0.05 s and 2.5 to 2.6 s at 0.025 s on this container, about 26 s of CPU in all, which `make check` spreads across its workers.

**Why it matters.** The comment above `EXACT_STEP_ORACLE_TOLERANCE` and `docs/MODEL.md` § "Independent-solution test" set the tolerance's 6.8-fold margin against 5.89e-14 as the worst residual measured. That maximum was taken over three of the five trajectories at the finer steps, so it was not shown to be the maximum, and the held corner came within 8% of it. A change that stopped the shipped step being exact only on ordinary use or the held corner, and only at a finer step, would also pass the finer-step test.

**Done when.** `test_the_disagreement_does_not_shrink_with_the_step` drives every trajectory in `ALL_GATE_TRAJECTORIES` at 0.1 s, 0.05 s and 0.025 s. Its docstring, the comment above `EXACT_STEP_ORACLE_TOLERANCE` and `docs/MODEL.md` § "Independent-solution test" state the measured figures over all fifteen pairs, including how many peak at the finest step and how many peak in a run's last 1.5 s. The tolerance does not change.

**Not in scope, and why.** Three ventilator starts in a row reach 2.46e-14 at 0.1 s against 1.39e-14 for one, because rounding accumulates with the number of steps. The gate exists to catch a return of method error, which is nine orders of magnitude larger than this, and `test_the_shipped_step_reaches_the_pinned_reference_horizons` already bounds an hour of accumulated rounding at held settings. So the longer turning run stays documented as a limit of a 600 s gate, as `docs/MODEL.md` already states it, and is not added as a test.
