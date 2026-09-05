---
id: PL-C4PH
title: Record the history sampling cadence as a decision of its own, separate from the integration step
priority: P2
effort: S
status: ready
classes: docs, refactor
feature: teachable-case
touches: docs/MODEL.md, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py
added: 2026-09-05
verify: python3 tools/doc_check.py check && grep -qF 'recorded-sample cadence' docs/MODEL.md
---

**Problem.** One number, `app.simulation_view.SIMULATION_STEP_S = 0.1`, answers
two independent questions, and only one of them is documented. It is the
integration step, justified at length in `docs/MODEL.md` §§ "Supported
simulation step" and "Displayed precision" as the operator split's
applicability-domain ceiling. It is *also*, silently, the recorded-sample
cadence: `SimulationController.advance()` records one `SimulationHistorySample`
per `advance()`, so the run's history is written at 10 Hz because the solver
steps at 10 Hz, and for no other stated reason. No document says the recording
cadence is a decision at all, so a reader cannot tell whether 10 Hz recording
is required or incidental.

**Why it matters.** The two questions have different answers and different
costs, and conflating them hides both.

- The step is bounded by solver error today, and by determinism afterwards:
  `ROADMAP.md` fixes it at 0.1 s at every playback multiplier for
  reproducibility and forking, and the control-input timeline quantises every
  recorded setting change to a step boundary, so the step also sets how
  faithfully a slider drag is recorded. Those reasons survive `PL-GS5X`
  (replace the operator split with the exact matrix exponential), which
  removes the accuracy reason entirely.
- The recording cadence is bounded by nothing but the timescales the run has
  to be readable at. The coupled system's fastest mode is 12.1-12.7 s at the
  reference adult's defaults and 5.3-6.2 s at the settings-envelope corner
  (measured under `PL-JDX0`, state the coupled system's modal time constants),
  so 10 Hz records 53 to 127 samples per fastest time constant — roughly an
  order of magnitude finer than a visually exact polyline needs, and nothing
  in the model varies faster, since ventilation is a continuous flow rather
  than tidal breaths.
- Only the recording side costs anything. `advance()` measures 17.8 us
  (2026-09-05, matching `PL-011`'s 19 us), so stepping at 10 Hz is 0.018% of a
  core in real time and 4.3% at the 12-hours-in-3-minutes playback v0.4.0
  wants. History is 264 B per sample: 0.11 GB at 12 h, 1.6 GB at a week, about
  6.6 GB at the owner's 30-day cap. The waste is entirely in what is kept, not
  in what is computed.

**What actually binds the cadence (measured 2026-09-05).** The model was
stepped at 0.1 s unchanged, its recorded samples then thinned to every Nth and
rejoined with straight lines the way the chart draws them, and the worst
disagreement against the full 0.1 s trace taken over every bucket phase, in the
percentage points the readout is in (display resolution 0.01 pp). Dial at the
agent's maximum for 600 s, then off, then 600 s of washout:

| Settings | Agent | Record every | circuit | alveolar | mixed venous | vessel-rich |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| default | sevoflurane | 0.5 s | 0.0106 | 0.0001 | 0.0000 | 0.0000 |
| | | 1.0 s | 0.0221 | 0.0003 | 0.0000 | 0.0000 |
| | | 2.0 s | 0.0439 | 0.0011 | 0.0001 | 0.0001 |
| corner | desflurane | 0.5 s | 0.0595 | 0.0012 | 0.0001 | 0.0001 |
| | | 1.0 s | 0.1229 | 0.0046 | 0.0002 | 0.0003 |
| | | 2.0 s | 0.2422 | 0.0171 | 0.0009 | 0.0014 |

**The worst error is at t = 600 s in every row — the instant the dial moves —
and it scales as O(h) rather than O(h^2).** That is the signature of a kink:
the derivative of the circuit fraction is discontinuous at a control change,
and linear interpolation across a bucket spanning one loses first-order
accuracy. Away from a control change the smooth trajectory is faithful to
about 1e-3 pp even at a 2 s cadence, a tenth of the display resolution, which
matches the coupled system's fastest mode of 5.3-12.7 s (`PL-JDX0`, state the
coupled system's modal time constants).

So the cadence is not set by the physiology. It is set by the two gas
compartments at a vaporizer change - which is exactly the moment a teaching
run exists to show.

**What this item is not.** Not a proposal to record every Nth step. Uniform
decimation at the recording layer would discard each bucket's extremes before
`chart_downsampling`'s M4 selection ever sees them, reintroducing exactly the
error class the chart cites Jugel et al. 2014 to avoid, one layer upstream —
a learner could read a transient off a trace the run never produced. The
memory answer is `PL-011` (bound the controller's concentration history), whose
own note already has the right shape: evict raw samples once a cached tier fine
enough for the narrowest scale has consolidated them. This item is the
statement that makes that policy decidable rather than the policy itself.

**Decided 2026-09-05 (project owner): chart-faithful only.** The requirement
this item exists to state is that **the drawn chart** must reproduce a control
change to the last displayed digit; **the stored record** need not, and may
coarsen behind a retention horizon. Requiring it of the stored record too would
pin retention at 10 Hz for the life of a run and leave `PL-011` (bound the
controller's concentration history) with nothing to work with.

Two consequences, and the second is not free.

- `PL-011` is unblocked on its requirement: raw samples become evictable once a
  cached tier fine enough for the narrowest time base has consolidated them,
  and the horizon is a memory decision rather than a fidelity one.
- **`chart_downsampling`'s M4 selection does not yet deliver the guarantee this
  decision rests on.** M4 keeps each bucket's extremes, and a dial turned *down*
  makes the kink a local maximum that M4 lands on exactly - but a dial turned
  *up* mid-rise leaves the trace monotone, so no tuple lands on the change and
  the polyline is drawn straight through it, at 0.02 to 0.08 pp depending on
  bucket width. `PL-4RBD` (the drawn chart smooths through a control change that
  leaves the trace monotone) is that defect and its fix - union the recorded
  `ControlChange.sample_index` values into the drawn set. It has to land before
  a retention horizon does, because after this decision the drawn line is the
  whole guarantee.

**Where.**

- `src/anesthesia_sim/app/simulation_view.py:86-97` — the comment block above
  `SIMULATION_STEP_S`, which explains the constant only as an integration step.
- `src/anesthesia_sim/app/controller.py` — `advance()`, where the recording is
  bound to the step by nothing but adjacency.
- `docs/MODEL.md` — a statement of the recorded cadence beside "Supported
  simulation step", saying what the recorded history is for and what
  resolution that requires.

**Done when.** `docs/MODEL.md` states the recorded-sample cadence as its own
decision, with the timescale that justifies it, and says explicitly that it
coincides with the integration step today rather than being determined by it;
`SIMULATION_STEP_S`'s comment says which of the two roles it is playing at each
use; and `PL-011` can be decided against a written requirement rather than
against an implementation accident.

**The third clause is void, and half of this item has a shelf life (triage,
2026-09-05).** `PL-011` is `dropped` — superseded by `PL-T691` and `PL-2FM6`,
which remove the store rather than bound it — so nothing is waiting on the
requirement in order to pick a retention horizon. Read the **Done when** as its
first two clauses only. Further out, `PL-2FM6` (delete `RunHistory` and draw the
chart from the closed-form sampler) deletes the recorded sample series outright,
at which point there is no recorded-sample cadence left to document and
`SIMULATION_STEP_S` is playing one role again rather than two. So the
cadence-as-a-separate-decision half is worth writing only while the sample store
exists, which is until `PL-GS5X` -> `PL-T691` -> `PL-2FM6` land.

**What is durable here is the requirement, not the cadence.** The owner's
decision recorded above — the **drawn chart** must reproduce a control change to
the last displayed digit, the **stored record** need not — survives both
architectures, and today it is written down nowhere but in this item's brief.
`PL-2FM6`'s own **Done when** already restates it as "a control event inside the
visible window always gets its own column", and `PL-4RBD` is the live defect
against it. Put that requirement into `docs/MODEL.md` as a statement about the
chart, so it outlives the mechanism this item was opened to describe; that
sentence is what makes the rest of the item safe to let expire.

**Sequencing.** After `PL-JDX0` (state the coupled system's modal time
constants), which supplies the timescale this cites — recorded as prose rather
than as a `blocked-by` edge, deliberately: both are `P2`, and a hard block on a
`P2` docs item would let a time-limited item expire unworked. The former
"before `PL-011`" edge is gone with that item's drop.
