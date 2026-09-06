---
id: PL-NBCJ
title: Decide whether MAXIMUM_SIMULATION_STEP_S should move to 0.05 s so an abrupt manoeuvre's timing stays inside one parameter SD
status: untriaged
added: 2026-09-06
---

**Problem.** Decide whether MAXIMUM_SIMULATION_STEP_S should move to 0.05 s so an abrupt manoeuvre's timing stays inside one parameter SD

**Why it matters.**

**Where.**

**Done when.**

**Decision wanted.** `MAXIMUM_SIMULATION_STEP_S` stays at 0.1 s after
`PL-X9KD`'s re-derivation, and the derivation records honestly that this does
not hold every manoeuvre inside its own criterion.

Measured 2026-09-06, worst displacement of a displayed compartment when a
control change lands one step late, in percentage points of one atmosphere,
desflurane binding throughout:

    case opening, dial off to 1 MAC at reference flows   6.7e-3 pp
    unperfused load, then perfusion on and dial off      5.0e-2 pp
    ventilator start at the envelope corner              1.4e-1 pp

The criterion these are read against is the model's own parameter uncertainty:
one SD of a measured partition coefficient moves a displayed compartment by
9e-4 to 6.8e-2 pp. So an ordinary dial change is timed to about a tenth of one
SD, and an abrupt ventilation change to about twice one SD. Halving the step to
0.05 s would bring the ventilator start just inside one SD, since the
displacement is exactly linear in the step.

**What it costs.** Twice the propagations per simulated second, and the
interface's tick structure would have to be revisited -
`SIMULATION_TICK_INTERVAL_S` is assigned from `SIMULATION_STEP_S`, and
`steps_per_tick` is derived from the ratio, so halving the step at a fixed
wakeup doubles the steps per tick at every playback rate. `PL-NBWP` is the
related finding and should probably be decided first, since it concerns the same
burst.

**Recommendation.** Leave it at 0.1 s unless `PL-NBWP` is resolved by changing
the burst, in which case revisit both together. The disclosure is already in
`docs/MODEL.md` § "Supported simulation step", so nothing is currently
overclaimed.

**Found.** `PL-X9KD`, 2026-09-06.
