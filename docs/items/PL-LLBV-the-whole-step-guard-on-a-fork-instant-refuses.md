---
id: PL-LLBV
title: The whole-step guard on a fork instant refuses 35.5% of the one-decimal times a user could type
priority: P2
effort: S
status: ready
classes: defect, ux
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py
added: 2026-09-14
verify: grep -q 'def test_a_one_decimal_fork_instant_is_accepted' tests/integration/test_controller.py && uv run pytest tests/integration/test_controller.py
---

**Problem.** The whole-step guard on a fork instant refuses 35.5% of the one-decimal times a user could type

`SimulationController._resume_point_at` requires the fork instant to be a whole
number of the run's steps, so that the branch can continue the case's step
count exactly:

```python
step_count = round(elapsed_s / simulation_step_s)
if step_count * simulation_step_s != elapsed_s:
    raise SimulationConfigurationError(...)
```

The guard is correct and should stay: a branch whose step count did not land on
the case's would not continue it. What it refuses is the point.

**Measured 2026-09-14 at the shipped 0.1 s step.** Of the 864 001 instants
`k * 0.1` that a run can actually stand at across a 24 h case, **0 fail**. Of
whole seconds 0 to 86 400, **0 fail**. But of the one-decimal times a user
would type — 0.0 to 3600.0 s — **12 767 of 36 001 fail (35.5%)**, the first
being 0.3, 0.6, 0.7, 1.2 and 1.4 s: `453 * 0.1 == 45.3` is `False`, and
`round(45.3 / 0.1) * 0.1` is 45.300000000000004.

**So it is not a defect today and becomes one with time bookmarks.** Every
instant reached by stepping passes, and today a fork instant only ever comes
from `run_segments`, which holds instants the run stood at. `PL-LPLD`'s time
bookmark is an absolute simulated time a learner *names*, and that is the first
input that can miss the grid while looking like it should not. The fix is at
the boundary that accepts the typed value — snap it to `round(t / step) * step`
once, where the user can see the instant that was taken — rather than by
loosening a guard whose exactness the branch's clock rests on.

**Reproduced 2026-09-14.** `SimulationController.fork_at`
(`app/controller.py`) documents the refusal - the instant "is
not finite, or is not a whole number of" steps. Tested against the shipped
0.1 s step over the one-decimal times from 0.1 s to 360.0 s: **1 235 of 3 600,
34.3%**, fail an exact whole-step test, because `12.3 / 0.1` is
`122.99999999999999` rather than `123`. The title says 35.5% over a different
range; the finding is the same and the order of magnitude is confirmed.

**Why it matters.** A third of the times a learner can type are refused, and
they are refused for a reason that has nothing to do with the model: the instant
is a valid fork point, and binary floating point cannot represent the division
exactly. `.claude/rules/expert-review.md` asks for interfaces that prevent
errors rather than warn after one, and this is the inverse - an interface
rejecting correct input and reporting it as the user's mistake. The pattern is
also one this project has already paid for once, in `PL-SM5V`: an exact
comparison over a quantity that reached the code through a unit conversion.

**Done when.** A fork instant the learner can express at the resolution the
interface offers is accepted whenever it names a real step - compared by
rounding to the nearest step and checking the residual against a stated
tolerance, or by taking the step index rather than the time - and the refusal is
reserved for an instant that genuinely falls between steps.
`tests/integration/` covers the one-decimal times that fail today.
