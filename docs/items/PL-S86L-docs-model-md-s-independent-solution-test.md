---
id: PL-S86L
title: docs/MODEL.md's independent-solution test section (about line 3913) still calls the unperfused load then dial off 'the worst trajectory the four sliders can reach', a ranking from the operator split; under the exact step and the 0.0125 s oracle it reports the least of the five gate trajectories (8.7985e-15 for desflurane against 1.5786e-14 for ordinary use, measured 2026-10-25 for PL-FJMW)
priority: P3
effort: M
status: done
classes: docs
feature: stale-source-claims
touches: docs/MODEL.md, tests/reference/test_coupled_dynamics.py
added: 2026-10-25
closed: 2026-10-25
payoff: The coupled model's verification section says which trajectory each gate figure comes from and where in a run the worst disagreement sits, as the exact step measures them today
verify: ! grep -qF 'four kinds of run' docs/MODEL.md && ! grep -qF 'worst trajectory the four' docs/MODEL.md && ! grep -qF 'always inside a' docs/MODEL.md && ! grep -qF 'same number of steps' docs/MODEL.md && ! grep -qF 'it alone exceeds the previous' docs/MODEL.md && ! grep -qF 'early in the wash-in' tests/reference/test_coupled_dynamics.py && ! grep -qF '6 000 for each of them' tests/reference/test_coupled_dynamics.py && ! grep -qF 'reached at about 306 s' tests/reference/test_coupled_dynamics.py && ! grep -qF 'always inside a' tests/reference/test_coupled_dynamics.py
---

**Problem.** docs/MODEL.md's independent-solution test section (about line 3913) still calls the unperfused load then dial off 'the worst trajectory the four sliders can reach', a ranking from the operator split; under the exact step and the 0.0125 s oracle it reports the least of the five gate trajectories (8.7985e-15 for desflurane against 1.5786e-14 for ordinary use, measured 2026-10-25 for PL-FJMW)

**Reproduced 2026-10-25.** `grep -n "worst trajectory the four" docs/MODEL.md` on `main` at `33a9a7bb` finds the sentence in § "Independent-solution test", in the bullet for the *unperfused load, then dial off*. It was written on 2026-08-30 under the operator split (`PL-SLHS`), when that trajectory did have the split's largest error coefficient.

**Re-scoped 2026-10-25, on starting it.** The same cause reaches ten more statements. Each was written under the operator split, or under the 0.05 s oracle that `PL-B1WW` replaced on 2026-09-07, and none was re-checked when the oracle converged. In § "Independent-solution test" of `docs/MODEL.md`:

1. "The gate therefore drives four kinds of run" lists four, but the gate drives five. *Ordinary use* is missing, though the section's own figures count five.
2. The ventilator start "alone exceeds the previous bound". That was the split's bound, and the sentence does not say so.
3. "the worst disagreement is always inside a transient", "at about 85 s" at held settings and "about 13 s later" across a setting change. These date from 2026-08-26, under the split (`PL-042`).
4. The five figures "lie within a factor of 1.8 ... because ... every trajectory takes the same number of steps". The unperfused load runs 900 s, which is 9 000 steps against the others' 6 000.
5. The paragraph opening "Both the corner and the worst trajectory are maxima by measurement" describes the split's coefficient sweep as if it described the exact step.

In `tests/reference/test_coupled_dynamics.py`:

6. The comment above `ENVELOPE_HORIZON_S` says the corner's worst disagreement occurs at 5.4 s, 6.6 s and 7.2 s, and that the running maximum is the same whether the run stops at 60 s or 3600 s. That was measured on 2026-09-06 under the 0.05 s oracle.
7. The comment above `SETTING_CHANGE_SCENARIOS` says that, re-measured under the exact step, the ventilator start's running maximum is reached at about 306 s and never approached again. That holds for sevoflurane only.
8. The tolerance comment above `EXACT_STEP_ORACLE_TOLERANCE` says the step count "is 6 000 for each of them".
9. The docstring of `_worst_error_over_phases` says that, except at held default settings, the worst disagreement is always inside a transient.
10. The docstring of `test_exact_step_matches_the_independent_solution_everywhere` says the same.

**Measured 2026-10-25** with `_worst_error_over_phases` at the shipped 0.1 s step and the 0.0125 s oracle. The script imported the test module and called the function directly, so it measured exactly what the gate measures. Each row gives the worst absolute disagreement, the simulated time at which it first reached that value, and the state it was in:

| Trajectory | Sevoflurane | Isoflurane | Desflurane |
| --- | --- | --- | --- |
| ordinary use | 1.1970e-15 at 499.0 s, circuit | 9.9486e-16 at 599.8 s, vessel rich | 1.5786e-14 at 598.5 s, vessel rich |
| reference point, held | 2.8935e-15 at 500.5 s, circuit | 3.9864e-15 at 600.0 s, vessel rich | 1.3427e-14 at 600.0 s, vessel rich |
| envelope corner, held | 1.2542e-15 at 600.0 s, muscle | 6.9077e-15 at 599.9 s, vessel rich | 1.5377e-14 at 600.0 s, vessel rich |
| ventilator start | 1.7590e-15 at 306.4 s, alveolar | 4.2917e-15 at 599.9 s, vessel rich | 1.3906e-14 at 599.6 s, vessel rich |
| unperfused load then dial off | 3.8025e-15 at 350.8 s, alveolar | 2.3662e-15 at 424.0 s, alveolar | 8.7985e-15 at 416.5 s, alveolar |

The desflurane column matches `PL-FJMW`'s figures to every digit. Nine of the fifteen peaks fall in the last 1.5 s of a 600 s run, where rounding has accumulated longest. Sevoflurane's two held-settings peaks fall near 500 s. The unperfused load's three fall in its loading phase, between 350.8 s and 424.0 s, long after the circuit and alveoli have saturated. Only sevoflurane's ventilator start peaks inside a transient, 6.4 s after ventilation starts. The function records the first time a new maximum is reached, so a peak at 600.0 s means every earlier value was smaller. A run stopped at 60 s therefore reports a smaller maximum, which refutes statement 6 outright.

**Why it matters.** `docs/MODEL.md` is the authoritative specification, and this section says what the coupled model's verification gate covers and why. The gate's failure message prints the instant and the state of the worst disagreement. A reader who believes the worst is always inside a transient will treat an end-of-run failure as anomalous. A reader who believes the unperfused load is the worst case will look in the wrong place. A reader who believes every trajectory takes the same number of steps has the wrong explanation of why the five figures sit close together.

**Done when.** Every statement listed above is true under the exact step and the converged oracle, or is marked as describing the operator split or the 0.05 s oracle. The section's list of trajectories names all five, *ordinary use* included. The section gives the measured peak times, or their pattern, and its explanation of why the five figures sit close together does not rest on equal step counts. The test file's comments and docstrings agree with `docs/MODEL.md` and with the table above. No test changes behaviour.

**Measured 2026-10-25, while checking the blind review's findings.** The same function at the two finer steps that `test_the_disagreement_does_not_shrink_with_the_step` drives, over the three trajectories it drives:

| Step | Trajectory | Sevoflurane | Isoflurane | Desflurane |
| --- | --- | --- | --- | --- |
| 0.05 s | reference point, held | 1.3385e-14 at 593.75 s, circuit | 9.6589e-15 at 437.05 s, circuit | 1.1213e-14 at 599.40 s, vessel rich |
| 0.05 s | ventilator start | 1.7777e-14 at 282.45 s, circuit | 1.2618e-14 at 599.95 s, vessel rich | 5.0099e-14 at 262.45 s, circuit |
| 0.05 s | unperfused load then dial off | 9.9087e-15 at 500.40 s, alveolar | 6.2103e-15 at 468.85 s, alveolar | 2.2038e-14 at 547.95 s, alveolar |
| 0.025 s | reference point, held | 3.8337e-14 at 600.00 s, vessel rich | 3.2876e-14 at 599.85 s, vessel rich | 7.8756e-15 at 579.85 s, circuit |
| 0.025 s | ventilator start | 2.5646e-14 at 273.03 s, circuit | 1.6133e-14 at 255.20 s, circuit | 5.8870e-14 at 236.08 s, circuit |
| 0.025 s | unperfused load then dial off | 1.5418e-14 at 586.23 s, alveolar | 9.8185e-15 at 599.98 s, alveolar | 3.6915e-14 at 565.80 s, alveolar |

So the end-of-run pattern holds at the shipped step only: two of the nine pairs at each finer step peak in the last 1.5 s. The ventilator start at 0.025 s peaks in the circuit while ventilation is still off, and desflurane's 5.8870e-14 there is the figure the tolerance is set against. At every step the unperfused load peaks in its loading phase. At 416.5 s of that phase, desflurane's mixed-venous, vessel-rich, muscle and fat fractions are exactly 0.0. Three ventilator starts in a row at 0.1 s give 2.4619e-14 for desflurane (at 903.2 s) and 7.4368e-15 for sevoflurane (at 1800.0 s, in muscle). The held corner at 0.025 s, which the step test does not drive, gives 5.4623e-14 for desflurane at 599.0 s. That last figure is the subject of `PL-F67Q`.

**Widened by the blind review, 2026-10-25.** Two blind passes found five more statements with the same cause, and each is fixed on this branch. Three test passages said muscle is never the worst state on a gate trajectory, but sevoflurane's held envelope corner peaks in muscle at 600.0 s. MODEL.md and the comment above `SETTING_CHANGE_SCENARIOS` said the two setting-change trajectories "bracket what a turning run does", but a longer turning run raises the residual. MODEL.md and the tolerance comment said the finer-step test drives "the same trajectories", but it drives three of the five. The retired-test history said the exact-step tolerance "is 6.45 times the worst residual", which was true of the 5e-12 bound of 2026-09-06 and not of today's 4e-13. The `HELD_RUN_ROUNDING_BOUND` comment gave a gate trajectory 6 000 steps, but the unperfused load takes 9 000. Whether the finer-step test should drive all five trajectories is a change to what the test checks, so it is `PL-F67Q`.
