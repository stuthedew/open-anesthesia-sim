---
id: PL-GFQD
title: tests/reference/test_coupled_dynamics.py holds its two rounding limits at 28 and 63 times the largest measured residual since the step-subdivision spread that set their margin can no longer be measured at one step length; derive each limit from the propagator's rounding bound or record why the margin stays
status: untriaged
feature: floating-point-domain
touches: tests/reference/test_coupled_dynamics.py, docs/MODEL.md
added: 2026-11-21
---

**Problem.** tests/reference/test_coupled_dynamics.py holds its two rounding limits at 28 and 63 times the largest measured residual since the step-subdivision spread that set their margin can no longer be measured at one step length; derive each limit from the propagator's rounding bound or record why the margin stays

**Where it was found.** `PL-SZ6G` (a run's time as a whole number of seconds), 2026-11-21. `EXACT_STEP_ORACLE_TOLERANCE` is 4e-13 and `HELD_RUN_ROUNDING_BOUND` is 1e-12. Their comments say that the margin above the measured residual covered the spread between steps of 0.1, 0.05 and 0.025 s. A run takes one step length now, and the test that measured the spread is deleted. At the one-second step the largest residuals are 1.43e-14 over 600 s and 1.58e-14 over an hour, so the limits allow 28 and 63 times what was measured, against 6.8 and 14 times before. A degradation of 1e-11 of the state still fails the first limit.

**What to decide.** The project owner's rule of 2026-11-14 is that a published error bound is derived and a measurement only checks it. `run_rounding` in `src/anesthesia_sim/core/rounding.py` gives the derived bound for a run of n steps. The test module may not import a solver from `core/`, and whether it may read the rounding module is the first question. One measurement to make first: several one-second residuals are as large as the 0.1 s ones although the run takes a tenth of the steps, which suggests that part of the residual is the independent solution's own rounding over its 48 000 steps. That is inferred and not measured.
