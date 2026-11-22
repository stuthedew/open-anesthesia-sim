---
id: PL-GFQD
title: tests/reference/test_coupled_dynamics.py holds its two rounding limits at 28 and 63 times the largest measured residual since the step-subdivision spread that set their margin can no longer be measured at one step length; derive each limit from the propagator's rounding bound or record why the margin stays
priority: P2
effort: M
status: done
classes: defect, test
feature: floating-point-domain
touches: tests/reference/test_coupled_dynamics.py, docs/MODEL.md, docs/VERIFICATION.md
deferred-from: v0.7.0 - a new problem: #2180 (d4e8200c, PL-SZ6G) moved every run to one step length and deleted the subdivision measurement that set the two margins
added: 2026-11-21
closed: 2026-11-22
pr: 2243
payoff: The reference test that shows the shipped step is accurate checks against a limit with a reason that still holds, so a real loss of accuracy cannot hide inside an inherited margin.
verify: ! grep -qF 'bound stays where the spread put it' tests/reference/test_coupled_dynamics.py
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

**Done 2026-11-22**, on `claude/project-thread-v9awbd`. Both limits keep their values, and each comment now gives a reason for its margin that still holds at the one-second step. Neither limit can come from `run_rounding`, because the derived bound is looser than the loss of exactness the test must catch.

1. **The derived bound is too loose to be the limit.** `run_rounding(3, StepCount(600))` is 1.07e-11 and `run_rounding(3, StepCount(900))` 1.60e-11, for the three trajectories at the envelope corner. `run_rounding(2, StepCount(3600))` is 3.20e-11 for the held hour. Each is a share of the state's scale, and each is at least the relative loss of 1e-11 that the Done-when names, so a limit set at it would pass that loss. So both limits stay fixed allowances, in the sense the docstring of `src/anesthesia_sim/core/rounding.py` gives the term. The question in § "What to decide", whether the test may read `core/rounding.py`, did not arise: the comment names the function and imports nothing.
2. **The spread still covers a one-second run, on `run_rounding`'s count.** Squarings counted on 2026-11-22 by wrapping `_squarings_for` in `core/matrix_exponential.py` while the module's own trajectories ran: at 1 s, two for ordinary use and the held reference point, three for the three corner trajectories. At 0.1, 0.05 and 0.025 s, none on any trajectory. So a one-second trajectory counts at most 0.8 times the steps-times-2^s of the same trajectory at 0.1 s (600 x 8 = 4 800 against 6 000; 900 x 8 = 7 200 against 9 000), and the hour 0.4 times (3 600 x 4 = 14 400 against 36 000). The subdivision spread was measured on runs of at least that count, so it is still a stand-in for platform variation at one second. That is an argument from the bound's scaling, not a measurement of platform variation, and the comment says "on the count that `run_rounding` makes".
3. **What each limit catches, re-measured.** Scaling every shipped state by (1 + 1e-11) with the test module's own `_worst_error_over_phases` and `_worst_state_error`: the five gate trajectories' worst rises to 1.8102e-12 and fails 4e-13. The held runs' worst is 4.6654e-13, which **passes** 1e-12. At (1 + 2.2e-11) the held worst is 1.0238e-12 and fails. So the held-run limit alone does not meet the Done-when; the gate limit does, and the Done-when asks only that "a test" fail. The comment and `docs/VERIFICATION.md` now say the held-run limit catches a coarser loss, and why: its runs hold the dial at 5%, so no fraction exceeds 0.05.
4. **The item's inferred measurement.** The brief suggested that part of the one-second residual is the oracle's own rounding. The squaring count explains the similar size instead: a 0.1 s step needed no squaring, and a one-second step needs two or three, so the bound per step rose by four to eight while the step count fell by ten. Not measured further.

Changed: the comments above `EXACT_STEP_ORACLE_TOLERANCE` and `HELD_RUN_ROUNDING_BOUND` in `tests/reference/test_coupled_dynamics.py`, and `docs/VERIFICATION.md` § "Independent-solution test" (the paragraph on the 4e-13 limit) and § "The tests and the figures behind the comparison" (the margin bullet, a new bullet on the loss the limit must catch, and the held-run bullet). The brief's `touches:` names `docs/MODEL.md`, where this text lived before #2232 to #2237 moved it to `docs/VERIFICATION.md`.

Files checked: `docs/VERIFICATION.md`, `docs/MODEL.md`, `docs/INTERFACE.md`, `docs/PARAMETERS.md` and `README.md`, by `grep -n "28 times\|63 times\|spread cannot be measured\|HELD_RUN_ROUNDING_BOUND\|EXACT_STEP_ORACLE_TOLERANCE"`. It found the `docs/VERIFICATION.md` passages that this item rewrote, which now give the reason beside the multiples, and `docs/INTERFACE.md` § "Displayed precision", which names the gate's constant as the limit to re-derive figures against. That is still right.
