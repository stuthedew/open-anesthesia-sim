---
id: PL-21V4
title: FreshGasFlow(10**400) and SimulationStep(10**400) raise Python's OverflowError rather than the simulator's own refusal, the shape PL-7N8P records for the case instant; no interface path reaches it (found triaging PL-7N8P)
status: dropped
feature: parse-dont-validate
added: 2026-10-04
closed: 2026-10-05
reason: half fixed by PL-LLMN (FreshGasFlow(10**400) is refused with SimulationConfigurationError, reproduced 2026-10-05); the surviving SimulationStep half is require_positive_finite's math.isfinite, folded into PL-3800, which rewrites that guard
---

**Problem.** FreshGasFlow(10**400) and SimulationStep(10**400) raise Python's OverflowError rather than the simulator's own refusal, the shape PL-7N8P records for the case instant; no interface path reaches it (found triaging PL-7N8P)

**Reproduced 2026-10-05, at triage: half of it no longer holds.** On Python
3.14.7, against `main` at `b67dace8`,

```bash
uv run python -c "from anesthesia_sim.core.supported_ranges import FreshGasFlow; from anesthesia_sim.core.simulation_step import SimulationStep
for build in (FreshGasFlow, SimulationStep):
    try: build(10**400)
    except Exception as e: print(build.__name__, type(e).__name__)"
```

printed `FreshGasFlow SimulationConfigurationError` and `SimulationStep
OverflowError`. The flow half was closed by `PL-LLMN`, whose closed-interval
comparison in `_require_supported` compares an `int` past the float range
exactly; `AlveolarVentilation`, `CardiacOutput`, `CaseInstant`, `Fraction` and
`Percent` refuse it the same way. The step half survives because
`SimulationStep` is built on `require_positive_finite` in
`core/validation.py`, whose `math.isfinite` raises the `OverflowError` - the
guard `PL-3800` rewrites for the same family of holes. Dropped into `PL-3800`,
whose Done when now names `SimulationStep(10**400)`, rather than kept as a
second change to the same two lines.
