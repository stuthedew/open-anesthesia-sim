---
id: PL-7CY5
title: Run a design round on computing a run by one rule: one exact step per whole second, every state stored, and time held as a whole number of seconds
status: untriaged
feature: standing-weight
added: 2026-11-20
---

**Problem.** Run a design round on computing a run by one rule: one exact step per whole second, every state stored, and time held as a whole number of seconds

**Why it matters.** The simulator computes a run's state in three ways: by stepping at 0.1 s (`SIMULATION_STEP_S` in `src/anesthesia_sim/app/dashboard_frame.py`), by `RunDefinition.state_at`, and by the display's `evaluate` and `evaluate_anchored`. The module docstring of `src/anesthesia_sim/core/run_definition.py` says that the three agree only to rounding, so each place that compares two of them needs a tolerance. `PL-GJ1W` (each comparison of computed values picks its own tolerance) counts 13 tolerance constants and is still producing items. An instant is a `float`, as `CaseInstant` in `src/anesthesia_sim/core/supported_ranges.py` shows. `PL-WKKH` (the streamlining questions from the study of the one-shot rewrite) holds the measurements and the sources.

**The design to weigh.** The one-shot rewrite, `stuthedew/OAS-Sim-oneshot` at commit `2f37877`, has one rule. Each whole second is one exact step of the linear system, and every state is stored. Charts and readouts read the stored states. A branch copies its parent's states. Time is a whole number of seconds. No two computed values are compared, so no tolerance is chosen. In it, a 24-hour run with a control change every hour computed in 0.6 seconds and held 6.9 MB. Both versions stop a run at 24 hours.

**Answered 2026-11-20.** The owner agreed to open this round before more work goes into `PL-GJ1W` (project owner, 2026-11-20, ratified, "Agree with recs", over continuing with the pull requests planned for `PL-GJ1W` first).

**What the round does first.**

1. Count the closed items that came from two paths disagreeing, or from a floating-point instant.
2. Measure how long a 24-hour run takes at one step per second in this code.
3. Say what the roadmap's nitrous oxide, concentration and second-gas effects need from the stepping rule. They make the equations non-linear, and a closed-form solution exists only for linear ones.

**Decision needed.** Should a run be computed by one rule? The choice is the owner's, because it changes `core/` and what a learner sees. A control change would land on a whole second, where today it lands on a tenth. The round brings its counts and a recommendation with the question.

**Done when.** The owner has the round's counts and its recommendation, and has answered.
