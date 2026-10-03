---
id: PL-5F76
title: A simulation step below about 4.8e-304 s, or a step count too long to print, fails SimulationState construction with OverflowError or ValueError rather than SimulationConfigurationError
status: untriaged
feature: numerical-domain
added: 2026-10-03
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
