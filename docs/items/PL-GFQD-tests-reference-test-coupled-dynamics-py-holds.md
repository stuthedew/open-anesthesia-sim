---
id: PL-GFQD
title: tests/reference/test_coupled_dynamics.py holds its two rounding limits at 28 and 63 times the largest measured residual since the step-subdivision spread that set their margin can no longer be measured at one step length; derive each limit from the propagator's rounding bound or record why the margin stays
priority: P2
effort: M
status: ready
classes: defect, test
feature: floating-point-domain
touches: tests/reference/test_coupled_dynamics.py, docs/MODEL.md
deferred-from: v0.7.0 - a new problem: #2180 (d4e8200c, PL-SZ6G) moved every run to one step length and deleted the subdivision measurement that set the two margins
added: 2026-11-21
payoff: The reference test that shows the shipped step is accurate checks against a limit with a reason that still holds, so a real loss of accuracy cannot hide inside an inherited margin.
---

**Problem.** tests/reference/test_coupled_dynamics.py holds its two rounding limits at 28 and 63 times the largest measured residual since the step-subdivision spread that set their margin can no longer be measured at one step length; derive each limit from the propagator's rounding bound or record why the margin stays

**Where it was found.** `PL-SZ6G` (a run's time as a whole number of seconds), 2026-11-21. `EXACT_STEP_ORACLE_TOLERANCE` is 4e-13 and `HELD_RUN_ROUNDING_BOUND` is 1e-12. Their comments say that the margin above the measured residual covered the spread between steps of 0.1, 0.05 and 0.025 s. A run takes one step length now, and the test that measured the spread is deleted. At the one-second step the largest residuals are 1.43e-14 over 600 s and 1.58e-14 over an hour, so the limits allow 28 and 63 times what was measured, against 6.8 and 14 times before. A degradation of 1e-11 of the state still fails the first limit.

**What to decide.** The project owner's rule of 2026-11-14 is that a published error bound is derived and a measurement only checks it. `run_rounding` in `src/anesthesia_sim/core/rounding.py` gives the derived bound for a run of n steps. The test module may not import a solver from `core/`, and whether it may read the rounding module is the first question. One measurement to make first: several one-second residuals are as large as the 0.1 s ones although the run takes a tenth of the steps, which suggests that part of the residual is the independent solution's own rounding over its 48 000 steps. That is inferred and not measured.

**Checked 2026-11-22**, at `d4e8200c`. `grep -n 'EXACT_STEP_ORACLE_TOLERANCE = \|HELD_RUN_ROUNDING_BOUND = ' tests/reference/test_coupled_dynamics.py`
printed `4e-13` at line 854 and `1e-12` at line 931. The comments above them
still say that each bound "stays where the spread put it" and that the spread
cannot be measured at one step length. So the fault is present.

**Why it matters.** These two limits are what the reference test uses to say
that the shipped step solves the equations it claims to. A limit 28 to 63 times
the measured residual, kept for a reason that no longer applies, lets a real
loss of accuracy of up to that size pass unseen. The project owner's rule of
2026-11-14 is that a published error bound is derived, and a measurement only
checks it.

**Who decides.** The question in § "What to decide", whether this test may
read the bound from `core/rounding.py`, is about how a test is built, so it is
the working session's call and not the owner's.

**Done when.** Each of the two limits either comes from a derived rounding
bound for the run it checks, or its comment gives a reason for its margin that
still holds at the one-second step. A test still fails a shipped state scaled
by (1 + 1e-11).

**Generator check.** The fact is how far a computed value can be from the
exact one, and so what a comparison on it proves. `PL-GJ1W` (every rounding
bound in one place) states it and is still open, so this is one more instance
under that head and not a re-entry.
