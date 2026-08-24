---
id: PL-042
title: Bound the splitting error across the settings envelope, not one point
priority: P1
effort: S
status: ready
classes: safety, science
touches: docs/MODEL.md, tests/reference/test_coupled_dynamics.py
added: 2026-08-24
---

**Problem.** `tests/reference/test_coupled_dynamics.py` bounds the
first-order splitting coefficient at one operating point — 5% delivered,
4 L/min fresh gas, default ventilation and cardiac output — while
`docs/MODEL.md` § "Independent-solution test" presents the resulting
\(C_{\max} = 5\times10^{-4}\ \mathrm{s^{-1}}\) as a bound on the split. It
is not one: measured over the interface's own slider limits it reaches about
\(1.2\times10^{-3}\ \mathrm{s^{-1}}\), in a configuration three sliders can
produce.
**Why it matters.** The absolute error there is still small (0.012 percentage
points), so no displayed value is wrong today. The gap is in the gate: a
change that degraded the split at high flow would pass CI, because CI never
looks there. A release gate narrower than the reachable input domain is a
verification claim broader than its evidence.
**Where.** `tests/reference/test_coupled_dynamics.py` (`DELIVERED_FRACTION`,
`FRESH_GAS_FLOW_L_MIN`, `HORIZONS_S`, and the fixed patient defaults),
`docs/MODEL.md` § "Independent-solution test" and § "Displayed precision".
**First step.** Parameterize the oracle over delivered fraction, fresh gas
flow, alveolar ventilation, and cardiac output, then measure the corners
before choosing the new bound — the bound follows the measurement.
**Done when.** The gate bounds the coefficient over the settings the
interface can produce, and `docs/MODEL.md` states the domain it covers.
**Context.** `docs/WORKING_NOTES.md`, "Splitting error outside the gate's
operating point".
