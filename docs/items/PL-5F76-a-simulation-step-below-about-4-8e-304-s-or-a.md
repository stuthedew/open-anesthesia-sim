---
id: PL-5F76
title: A simulation step below about 4.8e-304 s, or a step count too long to print, fails SimulationState construction with OverflowError or ValueError rather than SimulationConfigurationError
priority: P3
effort: S
status: ready
classes: defect
feature: numerical-domain
touches: src/anesthesia_sim/core/supported_ranges.py, tests/unit/test_supported_ranges.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
payoff: an absurdly large step count is refused with the simulator's own configuration error, like every other out-of-range input, instead of a Python error raised from inside the guard
verify: grep -q 'def test_a_step_count_too_long_to_print_is_refused' tests/unit/test_supported_ranges.py
---

**Problem.** A simulation step below about 4.8e-304 s, or a step count too long to print, fails SimulationState construction with OverflowError or ValueError rather than SimulationConfigurationError

**Measured 2026-10-03** by the first review of #1292 (`PL-73ZN`, `PL-BMY5`),
and reproduced the same day under Python 3.14.7.

- **The step.** `require_supported_simulation_step` accepts any positive,
  finite step up to 0.1 s. Below `86_400 / sys.float_info.max`, about
  4.806e-304 s, `86_400.0 / simulation_step_s` overflows to `inf` and
  `maximum_step_count` raises `OverflowError` from `floor(inf)`:
  `SimulationState(step_count=0, simulation_step_s=4.7e-304)` raises it, and
  `4.9e-304` is accepted. Before #1292 the same error came from the first
  `advance()`; the construction guard moved it earlier rather than in.
- **The count.** `SimulationState(step_count=10**5000, simulation_step_s=0.1)`
  raises `ValueError` ("Exceeds the limit (4300 digits) for integer string
  conversion") while `require_supported_step_count` formats its refusal.

**Why it matters, and how much.** Nothing in the application reaches either:
it steps at 0.1 s, and a step count comes from a run's own steps. A caller
from a notebook or a test gets a Python error where every guard in
`core/supported_ranges.py` promises `SimulationConfigurationError`, so the
harm is to the contract rather than to a displayed value, and the failure is
an obvious one.

**Candidate fix.** The count is mechanical: compare first, and name the limit
without printing a count too long to print. The step is a decision rather than
a repair, because refusing a tiny step is a statement about the model's domain:
`docs/MODEL.md` § "Supported simulation step" bounds the step above only, and a
floor there needs its own argument, not merely the arithmetic one above.
Regression tests at `4.7e-304` and `10**5000` that fail today.

**Narrowed at triage, 2026-10-03.** The step half is `PL-YZ17`'s: pull request
1306 adds `MINIMUM_SIMULATION_STEP_S` and refuses a step below it, so this item
keeps the count half only, as `PL-TS7L` recorded. Reproduced on `main` at
triage: `SimulationState(step_count=10**5000, simulation_step_s=0.1)` raises
`ValueError` ("Exceeds the limit (4300 digits) for integer string conversion"),
and a step of `4.7e-304` s still raises `OverflowError` until 1306 merges.

**Done when.** `SimulationState(step_count=10**5000, simulation_step_s=0.1)`
raises `SimulationConfigurationError` naming the supported limit, without
printing a count too long to print, and a regression test pins it.
