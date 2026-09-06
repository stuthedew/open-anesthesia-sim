---
id: PL-NBCJ
title: Decide whether MAXIMUM_SIMULATION_STEP_S should move to 0.05 s so an abrupt manoeuvre's timing stays inside one parameter SD
priority: P1
effort: S
status: needs-decision
classes: science
feature: numerical-domain
touches: src/anesthesia_sim/core/uptake_system.py, docs/MODEL.md, src/anesthesia_sim/app/simulation_view.py
added: 2026-09-06
---

**Problem, and the decision wanted.** `MAXIMUM_SIMULATION_STEP_S` stays at 0.1 s after
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

**Why it matters.** The step bound is not an implementation detail here; since
`PL-X9KD` it is a *declared* tolerance on how finely a control change is timed,
stated in `docs/MODEL.md` and measured in percentage points of displacement of a
value the interface shows. So the question this item poses is how much timing
error the application is willing to put on screen without saying so, against the
only honest yardstick available — the model's own parameter uncertainty. At
0.1 s an abrupt ventilation change is timed to about twice one SD of a measured
partition coefficient, which is the one case where the step contributes more
error than the parameters do. That is small in absolute terms and it is
disclosed, which is why the recommendation above is to leave it; it is still a
declared clinical-output tolerance, which is why it does not sit in a lower
band.

**Where.** `src/anesthesia_sim/core/uptake_system.py`'s
`MAXIMUM_SIMULATION_STEP_S` and the comment deriving it; `docs/MODEL.md`
§ "Supported simulation step"; and, if the step moves,
`src/anesthesia_sim/app/simulation_view.py`'s `SIMULATION_TICK_INTERVAL_S` and
`SIMULATION_STEP_S`, from whose ratio `steps_per_tick` is derived.

**Blocked on `PL-NBWP` at triage, 2026-09-06** — transcribing this item's own
"should probably be decided first", not a new judgment. Both concern the same
tick burst, and `PL-NBWP`'s options include changing it; deciding this one first
would either be undone by that answer or would silently constrain it. The block
is one-directional: `PL-NBWP` can be answered without this item.

**Unblocked 2026-09-06: `PL-NBWP` was decided, and it decided to leave the
burst alone.** So this item's own recommendation - "leave it at 0.1 s unless
`PL-NBWP` is resolved by changing the burst" - now points at leaving it, and
the condition that would have reopened it did not occur. Its "What it costs"
paragraph stands unchanged: `SIMULATION_TICK_INTERVAL_S` is still assigned from
`SIMULATION_STEP_S`, so halving the step still doubles the steps per tick at
every rate.

**What `PL-NBWP` adds to the case, and it argues the same way.** It measured
that the interface's own control resolution is `multiplier x 0.1` s rather than
0.1 s, so at every rate above 1x the *playback grid* already dominates the step
by a factor of the multiplier - 30 s at 300x against the 0.1 s this item would
halve. Halving the step would therefore improve the timing of an abrupt
manoeuvre only for a reader watching at 1x, which is a real case and a narrow
one, and it would leave the 300x figure untouched. It also measured that frames
are two grid steps apart at every rate, which is the reason `PL-NBWP` gives for
not tightening the grid and applies here unchanged: a step of 0.05 s would
resolve control timing to half of what the display can show even at 1x.

Read together, the recommendation is unchanged and now has a second reason
behind it.

**Decision needed.** Whether `MAXIMUM_SIMULATION_STEP_S` moves to 0.05 s so
that a reader at 1x playback, comparing an abrupt ventilation change against a
measurement, gets its timing inside one parameter SD rather than at about twice
one - at the cost of twice the propagations per simulated second and a revisit
of the interface's tick structure. `PL-NBWP` narrowed this to the 1x case and
did not settle it: above 1x the playback grid dominates the step by the
multiplier, so halving the step would not move the figure any faster reader
sees. The recommendation above stands - leave it at 0.1 s, since the
disclosure in `docs/MODEL.md` § "Supported simulation step" means nothing is
overclaimed - but it is the owner's call because it decides a declared
clinical-output tolerance.

**Done when.** `PL-NBWP` is answered, and then either the step moves to 0.05 s
with `SIMULATION_TICK_INTERVAL_S` and `steps_per_tick` revisited together and
`docs/MODEL.md`'s derivation re-stated, or it stays at 0.1 s and the decision is
recorded beside the constant — that the ventilator-start case is timed to about
twice one parameter SD, that this was accepted, and why.

**Found.** `PL-X9KD`, 2026-09-06.
