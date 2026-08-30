---
id: PL-VP7N
title: Refuse a simulation step outside the operator split's applicability domain
priority: P1
effort: M
status: done
classes: safety
feature: numerical-domain
milestone: v0.2.7
touches: src/anesthesia_sim/core/respiratory_system.py, src/anesthesia_sim/core/simulation.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md, tests/reference/test_coupled_dynamics.py, tests/reference/test_sevo_patient.py, tests/integration/test_controller.py, tests/unit/test_simulation.py, tests/unit/test_simulation_view.py
added: 2026-08-30
closed: 2026-08-30
commit: 82813bf
pr: 71
verify: uv run pytest -k maximum_simulation_step
---

**Problem.** `core/` accepts any simulation step and returns a plausible wrong
number. `docs/MODEL.md:560-561` states the operator split "has an applicability
domain, and stepping outside it must fail rather than produce a number", but the
only check on the step is `require_positive_finite("simulation_step_s", ...)` at
`core/respiratory_system.py:138`, which has no upper bound. Measured over 600 s
of sevoflurane wash-in, against the same run at the shipped 0.1 s step:

| Step | Alveolar error at 600 s |
| --- | --- |
| 1 s | 0.005 percentage points |
| 10 s | 0.060 percentage points |
| 30 s | 0.205 percentage points |

No error is raised at any of them. The 30 s figure is twenty times the 0.01
percentage-point resolution the interface displays, so the readout is wrong in
its *first* decimal while presenting itself as a settled value.
`SimulationNumericalError` first fires at dt=60 s, and it is a capacity guard —
a compartment driven negative — not a domain check: it happens to catch the
grossest case and says nothing about the range between.

**Why it matters.** The supported step is currently declared in the
presentation layer, `SIMULATION_STEP_S = 0.1` at `app/simulation_view.py:39`,
and restated a second time at `tests/reference/test_coupled_dynamics.py:339`
*without* the cross-check that `test_envelope_limits_match_the_interface`
(`:864`) gives the slider limits. So the one number that bounds the split's
validity is held in two places that cannot disagree loudly, and in neither of
them is it enforced. Any caller of `core/` — a future headless runner, a
notebook, a test — gets a number instead of a refusal. `CLAUDE.md`'s standard
is explicit that an obvious failure is preferred to a plausible-looking number
when correctness cannot be established; this is the path where that is not
true.

**Where.** `core/respiratory_system.py:138` (`advance`),
`core/simulation.py` (`SimulationState.advance`), `app/simulation_view.py:39`,
`docs/MODEL.md:560-566`.

**Decided approach.** A documented `MAXIMUM_SIMULATION_STEP_S` in core,
validated in `RespiratorySystem.advance` and `SimulationState.advance`, raising
`SimulationConfigurationError` — the caller's argument is refused and nothing
has been miscalculated yet, which is the distinction
`respiratory_system.py:141-152` already draws between a refused setting and an
untrustworthy run. `app/` imports the constant rather than declaring its own,
with a test pinning the two together the way
`test_envelope_limits_match_the_interface` pins the sliders.

**Not on the compartments.** The guard belongs on the coupled system, not on
`BreathingCircuit` or the individual compartments. A bare circuit stepped 60 s
is a single exponential with no splitting error at all, and
`tests/unit/test_circuit.py:35` and `:58` exercise exactly that; they must keep
passing unaltered.

**Blast radius.** Five existing call sites advance the coupled system outside
the domain and assert on the results. They are reworked to run inside it, never
exempted from the guard:

- `tests/integration/test_controller.py:178` and `:248`
- `tests/unit/test_simulation.py:11` and `:29`
- `tests/unit/test_simulation_view.py:815`

Also in scope: `test_step_refinement_converges`
(`tests/reference/test_sevo_patient.py:122`) compares two step sizes where
`docs/MODEL.md:856-862` specifies three (0.1, 0.05, 0.025).

**Relation to other items.** PL-SN2C (add the playback multiplier as steps per
tick) states this invariant as prose in its Safety notes — the multiplier "must
never change the step size… would also invalidate the error bound
`docs/MODEL.md` § 'Displayed precision' derives the two-decimal readout from".
That is the hazard written down; this item is what makes it true in code. Order
of work: this item, then PL-VM40 (derive simulated time from a step count),
then PL-SN2C, which depends on PL-VM40.

This is also finding P2-1 of `tools/review-verification/`, which has reproduced
since the v0.2.0 architecture review and was never captured — see PL-STNV
(retire the review-verification harness and capture its last live finding).

**Done when.** `core/` names a maximum simulation step with its derivation
recorded in `docs/MODEL.md`, both `RespiratorySystem.advance` and
`SimulationState.advance` refuse a larger one with
`SimulationConfigurationError`, `app/` imports that constant and a test pins the
two together, the five call sites above run inside the domain, the bare-circuit
tests pass unaltered, and the step-refinement test compares the three steps
`docs/MODEL.md` specifies.

---

**Updated 2026-08-30, after PL-SLHS landed.** That item (bound the splitting
error across setting changes) re-measured the coefficient this one's constant
must be derived from, and turned up a distinction the brief above does not
draw. Line citations refreshed at the same time; the two in "Why it matters"
had moved.

**The coefficient is measured and recorded.** \(C_{\max} =
2.29\times10^{-3}\ \mathrm{s^{-1}}\), in bold in `docs/MODEL.md`
§ "Independent-solution test". Do not re-derive it. `docs/MODEL.md`
§ "Supported input ranges" now also defines the reachable input domain, which
is the other half of "applicability domain" and was undocumented when this
item was written.

**Three different questions hide under "applicability domain", and they give
answers three orders of magnitude apart.** Measured on the worst reachable
trajectory (`_unperfused_load_then_dial_off`), all three agents:

| Criterion | Largest step it allows |
| --- | --- |
| Error stays within one count of the last displayed digit | **0.044 s** |
| First-order scaling still holds (C flat to ~1%) | ~5 s |
| The existing capacity guard fires | 15 s (iso), 30 s (sevo), 50 s (des) |

The first is below the shipped 0.1 s step. The second is useless as a safety
bound: C is flat there, but C·Δt is not — at 5 s the alveolar error is 1.12
percentage points, 112 counts of the last displayed digit. And C *falls* at
30 s for desflurane, to below its 0.1 s value, so a flat or falling
coefficient is not reassurance that the step is sound. The third is
agent-dependent by more than a factor of three, which is this item's own
complaint about it stated quantitatively.

**So the derivation is the decision, and it has a consequence worth raising
before building.** Inverting `docs/MODEL.md` § "Displayed precision" — the
largest step at which its claim about the last displayed digit stays true —
is the self-consistent choice, and at the worst trajectory it lands at or
just below the 0.1 s the interface ships. That leaves the supported step
equal to the shipped step, with no headroom for a coarser headless run.
Deriving it from ordinary use instead (C = 1.67e-4 s^-1 at 1 MAC and default
flows) gives 0.6 s, but then the constant no longer bounds the worst case it
is named for.

Neither is obviously right, and the choice changes what the constant means
rather than only its value. Put it to the project owner with a
recommendation before implementing, per `CLAUDE.md`'s rule on deliverables
that would differ materially from the one described.

**One thing the brief above gets slightly wrong.** It says
`SimulationNumericalError` "first fires at dt=60 s". On the worst reachable
trajectory it fires at 15 s for isoflurane. The point the brief was making —
that the guard is a capacity check rather than a domain check and says
nothing about the range below it — is unaffected and still correct.

---

**Resolved 2026-08-30.** The derivation question was put to the project
owner with a recommendation, per the update above, and answered: the bound
inverts `docs/MODEL.md` § "Displayed precision", giving
`MAXIMUM_SIMULATION_STEP_S = 0.1 s`. The supported step and the shipped step
are therefore the same number, with no headroom for a coarser headless run.
PL-10MX (advance a caller over a duration by taking supported steps) is what
serves that caller instead of refusing it, and was captured here.

**Three corrections to the update section, from re-measuring it.** The
oracle used was rebuilt at a fixed 0.005 s step rather than at half the step
under test, because halving is useless at multi-second steps; it reproduces
every pinned reference state to 5.5e-15.

- The update frames the display criterion as *one* count of the last
  displayed digit, which gives 0.044 s and lands below the shipped step.
  That is not the claim `docs/MODEL.md` makes. "Displayed precision" states
  a tiered uncertainty — a fifth of a count in ordinary use, half at a
  maximum dial, one at the envelope corner, about two on the worst
  reachable trajectory — and all four hold at 0.1 s (measured: 0.167, 1.207
  and 2.29 counts for the three that were checked). Inverting the section
  as written lands *exactly* at 0.1 s, not "at or just below" it. A
  one-count rule would also outlaw an ordinary ventilator start, which
  allows only 0.066 s under it.
- "First-order scaling still holds (C flat to ~1%)" allows 0.6 s for
  isoflurane and about 2.5 s for the other two, not ~5 s.
- The capacity guard first fires at 12 s (isoflurane), 25 s (sevoflurane)
  and 50 s (desflurane) on the worst trajectory, not 15/30/50. The
  update's point — agent-dependent by more than a factor of three — is
  strengthened rather than weakened: it is a factor of four.

**Two call sites the brief did not list** also advanced the coupled system
outside the domain: `tests/unit/test_simulation_view.py`'s 1 s step, and
`tests/unit/test_respiratory_system_failure.py`'s 60 s breakdown step. The
second needed rethinking rather than rescaling — no supported step can break
the split on the reference adult once the guard is in place, so the
numerical-error path is now reached through a compartment whose capacity one
supported step overdraws, which is what a future parameter set could produce.

**One deliberate departure from the decided approach.** The brief has `app/`
import the constant rather than declare its own. It declares
`SIMULATION_STEP_S = 0.1` instead, with
`test_the_shipped_step_is_within_the_maximum_simulation_step` asserting it is
`<=` the core bound. Aliasing a render cadence to a validity limit would mean
a future numerical method supporting a 5 s step silently made the interface
render at 5 s. The complaint the brief was making is still answered: the
bound lives in exactly one place, and every restatement of the step is now
checked — the reference suite's against the interface's by equality, the
interface's against core's by `<=`.

**Four paths outside the declared `touches`**, all deliberate:
`tests/unit/test_respiratory_system_failure.py` (a call site the brief did
not list, above), `docs/WORKING_NOTES.md` (the doc sweep — the PL-009
playback thread listed "how it interacts with the fixed `SIMULATION_STEP_S`"
as open, and half of that is now decided), and the two captured item files.

**Captured, not fixed here.**

- PL-0MLQ (refuse a setting outside the documented supported input range) —
  `core/` accepts a cardiac output of 1000 L/min and a fresh gas flow of
  500 L/min, though `docs/MODEL.md` § "Supported input ranges" declares
  closed intervals for all four controls and calls them the verification
  domain. This item's defect, one axis over.
- PL-10MX (advance a caller over a duration by taking supported steps) — the
  supported route for a caller who wants 30 s of simulated time, now that
  asking for it in one step is correctly refused.
- PL-0999 (`docket verify` defaults to a local `main` that a fresh checkout
  leaves stale) — found closing this item out: the default base reported 20
  paths outside the commission where `--base origin/main` reports 4.
