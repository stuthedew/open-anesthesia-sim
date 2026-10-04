---
id: PL-4R3W
title: Fraction and Percent are NewTypes, which the interpreter erases, so their ranges of 0 to 1 and 0 to 100 are checked by hand wherever a value enters - require_percent at four sites in circuit.py and governing_equations.py - the hand-checked pattern PL-51B7 replaces with checked types for the supported-range quantities; whether a concentration becomes a checked type too is undecided, because concentration.py chose NewTypes to catch a missing conversion, and whether a fraction computed at a bound can round past it is unmeasured
priority: P2
effort: M
status: needs-decision
classes: refactor
feature: parse-dont-validate
touches: src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/core/validation.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, tests, docs/MODEL.md
added: 2026-10-04
payoff: whether a concentration is checked once into a type, as the flows are, is answered on a measurement, so the eleven hand checks on its ranges are either replaced or kept for a recorded reason
---

**Problem.** Fraction and Percent are NewTypes, which the interpreter erases, so their ranges of 0 to 1 and 0 to 100 are checked by hand wherever a value enters - require_percent at four sites in circuit.py and governing_equations.py - the hand-checked pattern PL-51B7 replaces with checked types for the supported-range quantities; whether a concentration becomes a checked type too is undecided, because concentration.py chose NewTypes to catch a missing conversion, and whether a fraction computed at a bound can round past it is unmeasured

**Why it matters.** `Fraction` and `Percent` carry every concentration the
model computes and every dial a learner sets, both on the path to a displayed
clinical value. Their ranges are checked by hand: `require_fraction` at seven
call sites and `require_percent` at four, counted 2026-10-04 (the title's four
is `require_percent`'s alone). That is the pattern `PL-51B7` replaces for the
flows, the instants and the step count, and `PL-HSFV` is what it leaks.

**Decision needed.** Do `Fraction` and `Percent` become checked `float`
subclasses, each built only through its range check, as the flows become in
`PL-0YYV`?

**Recommendation: yes, once one measurement is in.**

- **They are ranges.** `core/simulation_step.py`'s module docstring, written
  when `PL-0GJC` chose a `float` subclass for the step, says a `NewType`
  "suits a unit, where every float is a valid value, and not a range".
- **Converting keeps what `concentration.py` chose `NewType`s for.** `mypy`
  holds two `float` subclasses apart as it holds two `NewType`s apart, so a
  missing conversion is still refused, and arithmetic on either still returns a
  plain `float`.
- **It removes the eleven hand checks**, each becoming its type's own.
- **The measurement comes first**, because wrapping a computed value in a
  checked type checks it. Record the extremes the exact step computes across
  the supported envelope's corners and the reference cases, at every place a
  computed value would be wrapped. If a fraction can round past 0 or 1 - a
  washed-out compartment at -1e-20, say - converting would refuse a run that
  runs today. Then that type stays a `NewType`, and `concentration.py` records
  the measurement as the reason.
- **`MacMultiple` stays a `NewType` either way**, being unbounded above by
  design.

**Done when.** The decision is recorded beneath the question, with the
measurement it rests on, and either the conversion it chooses has landed, the
hand checks it replaces deleted and `docs/MODEL.md` § "Concentrations" saying
where each range is enforced, or `concentration.py`'s module docstring says why
the type stays a `NewType`.

**Gate.** On v0.6.0's frozen list, in the product lane, with the rest of the
`parse-dont-validate` feature (project owner, 2026-10-04).

## Design round 2026-10-04

Run by the Ship v0.6.0 project's design thread, on `main` at `63bc149a` under
Python 3.14.7, with no code changed. The measurement the recommendation above
asked for is in, and it is recorded here in full because the type's whole case
rests on it.

**Measured 2026-10-04: where a computed fraction can go.** A recording `float`
subclass was bound in place of `Fraction` in `core/uptake_system.py` and
`core/circuit.py`, so that every value `_write_state_vector` and
`advance_fresh_gas` wrap was what the measurement saw; the exact path a chart
reads, `RunDefinition.state_at`, was sampled directly. The scratch script is
not committed; each part and its result:

1. **The floor cannot be crossed, by construction and by measurement.** The
   propagator is entrywise nonnegative in floating point - the section "The
   shift" of `core/matrix_exponential.py`'s docstring is the argument - so a
   state of nonnegative fractions stays nonnegative; the smallest propagator
   entry over 24 h at the widest supported flows is `0.0`. Washing out from
   saturation at each agent's dial maximum with the dial off, the smallest
   fraction over 1 h stepped at 0.1 s lay between `1.9e-45` and `9.5e-30`
   across the three agents at zero ventilation and at zero cardiac output,
   and over 24 h propagated exactly it was `0.0`, never negative. The
   circuit's own closed form washing out from 1.0 reached `2.2e-321` after a
   million steps and no lower; a tissue group's reached `4.8e-268`.
2. **Inside every agent's envelope the ceiling is the dial, far from 1.**
   The 48 corners - three agents, fresh gas flow 0 and 10 L/min, alveolar
   ventilation 0 and 12 L/min, cardiac output 0 and 10 L/min, the dial off and
   at the agent's maximum - each stepped 1 h at 0.1 s from empty and sampled
   every 60 s over 24 h on the exact path: the highest fraction anywhere was
   `0.18000000000002825`, desflurane at 18% with fresh gas 10, ventilation 0
   and cardiac output 10 L/min, on the exact path; the highest of the
   10 368 000 values the stepped path wrapped was `0.17999999999999464`. From
   saturation - every compartment standing at $`F_D`$, the fixed point - the
   exact path over 24 h drifts above $`F_D`$ by up to `1.4e-11` (desflurane,
   7.6e-11 of itself; 490 610 ulp), the stepped path over 1 000 s by up to
   `5.9e-13` (21 157 ulp). That drift is the shift's documented cost
   (`core/matrix_exponential.py`, "What it costs") and it is bounded by
   $`F_D \le 0.18`$ for every shipped agent, so no supported setting puts a
   fraction within `0.8` of the bound a checked type would refuse at.
3. **At a 100% dial, which no agent reaches, the exact path does cross 1.**
   Only a circuit built without an agent admits it, its maximum defaulting to
   100% (`BreathingCircuit`'s docstring: "only appropriate for a circuit built
   without an agent"). Standing at 1.0 and propagated exactly over 24 h, the
   highest fraction was `1.000000000099652` (sevoflurane, fresh gas 10,
   ventilation 0, cardiac output 10 L/min; 448 793 ulp above 1); washing in
   from empty, sampled on the exact path, reached `1.0000000000001568` at zero
   ventilation and `1.0000000000001397` at zero cardiac output. **The stepped
   path already refuses this today**: from saturation at 1.0, 10 of the 12
   corners halted within 10 000 steps with `SimulationNumericalError` naming a
   compartment ("alveolar partial_pressure_fraction must be between 0 and 1"),
   because `_write_state_vector`'s setters call `require_fraction` on the
   `1.0000000000000002` the propagator returned; the other two held exactly
   1.0. So a checked type changes nothing on the stepped path, and on the
   display path it would refuse, outside the supported envelope, a value the
   chart today formats as 100.00%.
4. **The read-back the controller's snapshot wraps stays inside.**
   `amount / capacity` for the 15 shipped capacities (for each agent, the
   alveolar gas volume, the venous capacity and the three tissue capacities)
   over 3 000 135 fractions, the edges included: none outside [0, 1].
   Rounding is monotone, so $`\mathrm{fl}(c f) \le c`$ for $`f \le 1`$ and
   the quotient cannot exceed `1.0`.
5. **The compartments' own closed forms stay inside.** `advance_fresh_gas`,
   `TissueGroup.advance` and `VenousBloodCompartment.advance`, each driven
   from 1.0 toward a random lower fraction over 200 000 trials: none above 1.0.
   Washing in toward a 100% dial over a million steps reached
   `0.99999999999995`; standing at 1.0 under a 100% dial stayed exactly `1.0`.
6. **The display conversions stay inside.** `percent_from_fraction` on a
   million fractions in [0, 1]: none above 100, and `Fraction(1.0)` gives
   `100.0` exactly; `fraction_from_percent` on a million percents in [0, 100]:
   none above 1.
7. **What it costs.** A `NewType` call is 55 ns, a checked `float` subclass
   240 ns, `require_fraction` alone 72 ns, all per construction, measured with
   `timeit`. `_write_state_vector` builds six per step, so the step pays about
   1 µs more against the 23.8 µs whole step `core/matrix_exponential.py`
   records in `propagate`'s docstring (`PL-R460`), around 4%; a chart paint
   pays one construction per plotted point.

**Recommendation (design round, 2026-10-04): yes, convert both.** The
measurement the brief made the condition is in: inside the supported envelope no
computed fraction leaves [0, 1], at either bound, on either path. The one case
that crosses - a 100% dial on a circuit built without an agent, where the exact
propagator's shift cost carries a saturated state about `1e-10` above 1 - is
outside `docs/MODEL.md` § "Supported input ranges" (the dial's range is 0 to the
agent's maximum), reachable from no application path, and already a halt on the
stepped path today. There the type would make the display path agree with the
stepped one, which is the safety-critical standard's own preference: an obvious
refusal over a 100.00000000001% presented as 100.00%. So the finding is recorded
as the type's documented limit rather than as a reason to keep a `NewType`, and
the brief's "then that type stays a `NewType`" does not fire.

The build, for the thread that takes it (nothing here is built in the round):

- `Fraction` and `Percent` in `core/concentration.py` become `float`
  subclasses on `SimulationStep`'s pattern (`core/simulation_step.py`):
  `__slots__ = ()`, a `__new__` that refuses a non-finite value or one outside
  the range with `SimulationConfigurationError`. `MacMultiple` stays a
  `NewType`, unbounded above by design.
- **The refusal keeps naming the value, where several can refuse.**
  `require_fraction`'s `name` is the whole of what a reader of the halted-run
  banner is told about which compartment refused (`core/validation.py`'s module
  docstring; `PL-SPN6` is what losing it cost). A constructor has no name, so
  the type takes the one the refusal is reported under, defaulting to its own
  word - the smallest form is a second argument,
  `Fraction(state[ALVEOLAR_FRACTION], "alveolar partial_pressure_fraction")` -
  and `_write_state_vector`, where six compartments' values are built, passes
  each compartment's as the setters do today. Catching the error in
  `_write_state_vector` and prefixing it was considered and refused: the
  sentence a reader sees should be readable in the line that raises it, which
  is the rule that docstring states. The exact signature is the builder's.
- `require_fraction` and `require_percent` leave `core/validation.py`, and
  their eleven call sites become a type check at each public entry point, as
  `require_simulation_step` is for the step: `TypeError` for a bare `float`,
  since `mypy` refuses one in `src/` and the check refuses one from `tests/`
  and from a value typed `Any`. `UptakeEquationSettings.__post_init__` drops
  `require_percent` and keeps the deliverability relation `PL-BBMG` gives it,
  which is a relation between two fields and not the quantity's own range.
- The wraps of computed values in `src/` keep their syntax and now check: four
  in `core/uptake_system.py`, five in `core/circuit.py`, six in
  `app/controller.py`, four in `app/chart_frame.py`, two in
  `app/dashboard_frame.py` for `Fraction`, and the `Percent` wraps in
  `core/circuit.py`, `core/parameters.py`, `app/controller.py`, `app/run_view.py`,
  `app/chart_frame.py`, `app/dashboard_frame.py`, `app/control_timeline.py`
  and `app/wash_in.py`; items 2 to 6 above are what says each stays in range.
- Docs: `core/concentration.py`'s module docstring loses "They are erased at
  runtime too" and gains what the constructor refuses and the 100% limit in
  item 3; `docs/MODEL.md` § "Concentrations" says the range is enforced by the
  type where a value is built and names the entry points that refuse a bare
  `float`; `.claude/rules/core-domain.md` § "A quantity with a check of its own
  is a type, checked once" rewrites its bullet calling the two `NewType`s;
  `core/simulation_step.py`'s and `core/parameters.py`'s docstrings naming
  them `NewType`s follow.
- Tests: `tests/unit/test_validation.py`'s `require_fraction` cases move to
  `tests/unit/test_concentration.py` as constructor cases at both edges and the
  IEEE 754 edges; a regression test pins that `Fraction(1.0000000000000002)` is
  refused under the name it was built with; the tests that drive a bare
  circuit at a 100% dial keep passing, since the halt they expect is the one
  the type now raises.
- Order: after `PL-0YYV` (slice 1), with which this shares
  `core/governing_equations.py`, `core/alveolar.py`, `core/circuit.py`,
  `core/uptake_system.py`, the tests and `docs/MODEL.md`, and after `PL-BBMG`,
  with which it shares `UptakeEquationSettings.__post_init__` - slice 1, then
  `PL-BBMG`, then this. Independent of slices 2 and 3. It changes nothing in
  slice 1, which types the flows and touches none of the eleven range checks.
- Size stays M: eleven guard sites, about thirty wraps whose syntax does not
  change, 56 `Fraction(` and `Percent(` calls in 15 test files, and the docs.
- `verify:`, to set at the answer:
  `! grep -q "def require_fraction" src/anesthesia_sim/core/validation.py && ! grep -q "def require_percent" src/anesthesia_sim/core/validation.py && grep -q "class Fraction(float)" src/anesthesia_sim/core/concentration.py && grep -q "class Percent(float)" src/anesthesia_sim/core/concentration.py`.
