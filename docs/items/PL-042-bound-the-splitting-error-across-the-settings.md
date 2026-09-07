---
id: PL-042
title: Bound the splitting error across the settings envelope, not one point
priority: P1
effort: S
status: done
classes: safety, science
milestone: v0.2.6
touches: docs/MODEL.md, tests/reference/test_coupled_dynamics.py
added: 2026-08-24
closed: 2026-08-26
commit: 1180158
pr: 57
---

**Problem.** `tests/reference/test_coupled_dynamics.py` bounds the
first-order splitting coefficient at one operating point — 5% delivered,
4 L/min fresh gas, default ventilation and cardiac output — while
`docs/MODEL.md` § "Independent-solution test" presents the resulting
$`C_{\max} = 5\times10^{-4}\ \mathrm{s^{-1}}`$ as a bound on the split. It
is not one: measured over the interface's own slider limits it reaches about
$`1.2\times10^{-3}\ \mathrm{s^{-1}}`$, in a configuration three sliders can
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
**Context.** The splitting-error thread this line cited was rewritten out of
`docs/WORKING_NOTES.md` as it resolved. `PL-X9KD` carries what became of it.

**Worked.** The bound follows the measurement, as the brief required, but two
things the brief did not specify were decided here.

*The gate now takes the maximum over the trajectory rather than comparing
endpoints.* The envelope's worst disagreement is at about 85 s, which no
endpoint at 60, 600 or 3600 s samples, so the old structure could not have
caught it whatever bound it carried. This costs 0.6 s of suite time because
the RK4 integration was already the expense.

*The margin is 1.24x rather than the 2x the previous bound used.* Both things
a wider margin buys are covered elsewhere - parameter revision fails the
pinned reference states first, and envelope variation no longer needs
absorbing - and a narrow margin is what keeps the gate consistent with the
displayed-precision claim it now cross-references.

Also added `test_envelope_limits_match_the_interface` and put `simulation_view`
on ALLOWED_PACKAGE_IMPORTS for it: restating the slider maxima recreates the
silent-decay risk this item exists to fix. The independence rule is unaffected
- what it forbids is importing a solver, and the oracle still uses the
parameter loaders alone.

