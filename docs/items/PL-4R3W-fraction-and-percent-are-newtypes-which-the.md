---
id: PL-4R3W
title: Fraction and Percent are NewTypes, which the interpreter erases, so their ranges of 0 to 1 and 0 to 100 are checked by hand wherever a value enters - require_percent at four sites in circuit.py and governing_equations.py - the hand-checked pattern PL-51B7 replaces with checked types for the supported-range quantities; whether a concentration becomes a checked type too is undecided, because concentration.py chose NewTypes to catch a missing conversion, and whether a fraction computed at a bound can round past it is unmeasured
priority: P2
effort: M
status: done
classes: refactor
feature: parse-dont-validate
touches: src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/core/validation.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/simulation_step.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/run_view.py, tools/core_vocabulary_check.py, .claude/rules/core-domain.md, tests, docs/MODEL.md, docs/ARCHITECTURE.md, docs/items/PL-T137-core-validation-py-rejects-a-value-without.md, docs/items/PL-HXKC-eight-of-the-twenty-three-public-functions-in.md, docs/items/PL-LLMN-require-supported-admits-0-0-shown-as-0-0-l-min.md
added: 2026-10-04
closed: 2026-10-05
pr: 1365
payoff: whether a concentration is checked once into a type, as the flows are, is answered on a measurement, so the eleven hand checks on its ranges are either replaced or kept for a recorded reason
verify: ! grep -q "def require_fraction" src/anesthesia_sim/core/validation.py && ! grep -q "def require_percent" src/anesthesia_sim/core/validation.py && grep -q "class Fraction(float)" src/anesthesia_sim/core/concentration.py && grep -q "class Percent(float)" src/anesthesia_sim/core/concentration.py
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

**Answered 2026-10-04: yes, both.** (project owner, 2026-10-04, ratified, over
keeping either as a `NewType` once the measurement came in; "Agree with recs"
in the project chat at 17:53 UTC, answering the design round's summary of
§ "Design round 2026-10-04" below). `Fraction` and `Percent` become checked
`float` subclasses on `SimulationStep`'s pattern and `MacMultiple` stays a
`NewType`. The 100% case the measurement found is recorded as the type's
documented limit, not as a reason to keep a `NewType`.

**Recommendation: yes, once one measurement is in.**

- **They are ranges.** `core/simulation_step.py`'s module docstring, written
  when `PL-0GJC` chose a `float` subclass for the step, says a `NewType`
  "suits a unit, where every float is a valid value, and not a range".
- **Converting keeps what `concentration.py` chose `NewType`s for.** `mypy`
  holds two `float` subclasses apart as it holds two `NewType`s apart, so a
  missing conversion is still refused, and arithmetic on either still returns a
  plain `float`.
- **It removes the eleven hand checks**, each becoming its type's own.
- [superseded 2026-10-04: the measurement is in, § "Design round 2026-10-04"
  below, and its condition did not fire] **The measurement comes first**,
  because wrapping a computed value in a
  checked type checks it. Record the extremes the exact step computes across
  the supported envelope's corners and the reference cases, at every place a
  computed value would be wrapped. If a fraction can round past 0 or 1 - a
  washed-out compartment at -1e-20, say - converting would refuse a run that
  runs today. Then that type stays a `NewType`, and `concentration.py` records
  the measurement as the reason.
- **`MacMultiple` stays a `NewType` either way**, being unbounded above by
  design.

**Done when.** `Fraction` and `Percent` in `core/concentration.py` are
`float` subclasses checked when built, with the 100% limit the measurement
found in the module docstring; `require_fraction` and `require_percent` are
gone from `core/validation.py` with their eleven call sites, each public entry
point that took a bare `float` refusing one with `TypeError`; and
`docs/MODEL.md` § "Concentrations" says the range is enforced by the type where
a value is built. `MacMultiple` stays a `NewType`.

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
8. **What the whole test suite constructs today.** The suite, 3 911 tests,
   ran green with recording `float` subclasses bound in place of both types in
   every `anesthesia_sim` module: 115 061 942 constructions at 83 sites, 28 of
   them in `src/`, and 11 outside the range, at five sites, every one
   deliberate. Two are `tests/unit/test_resume_at.py` handing the stepped path
   a state of 2.0 and of 1.5 to watch a setter refuse it
   (`uptake_system.py:658` and `:662`); the type refuses in the same statement,
   and `advance()` still reports it as a `SimulationNumericalError`. Four are a
   test tissue in `tests/integration/test_simulation_view.py` writing
   `Fraction(-1.0)` to make a step fail, which the build makes fail some other
   way. Four are `percent_from_fraction` on the impossible negatives
   `tests/unit/test_formatting.py` feeds `format_percent` and
   `format_mac_multiple` to see them left visible; a checked `Fraction` cannot
   carry one, so that guarantee moves to the constructor - an impossible value
   is refused where it is built rather than displayed, which is the
   safety-critical standard's own preference - and the two tests become
   constructor cases. One is `tests/unit/test_concentration.py`'s
   `Percent(150.0)`, there to show the `NewType` checks nothing, which
   inverts. Nothing a run or a chart computed was outside the range: the
   largest computed fraction on the stepped path was `0.17999812938938445`,
   the inspired fraction under an 18% dial, over 14 851 330 constructions at
   that site, and the largest the application built was `0.0801` in a chart.

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

## Close-out 2026-10-05

Built as the design round's list has it, in `#1365`, with four things a
reviewer would otherwise have to find:

- **Twelve call sites, not eleven.** `PL-BBMG` landed between the count and
  the build and gave `UptakeEquationSettings` a `require_percent` of its own
  for the vaporizer maximum, so twelve range checks left `core/validation.py`.
- **The type checks keep the pattern's names.** `require_fraction` and
  `require_percent` now live in `core/concentration.py` beside the types, as
  `require_simulation_step` and the three flow checks do, and check the type
  rather than the range. Each names a value of the other type as one and says
  to convert it, since a `Fraction` built from a percent's value is a
  hundredfold error that nothing downstream would refuse.
- **The name is a keyword argument**, `Fraction(value, name=...)`, defaulting
  to the type's own word, so the refusal still says which of the five
  compartments and the circuit refused (`PL-SPN6`). `_write_state_vector`
  passes each compartment's, and so does `app/run_view.py` for the dial.
- **Two `app/` files beyond the list.** `app/formatting.py`'s docstrings said
  an impossible negative was rendered with its sign; it is refused now, by
  `percent_from_fraction`, and the two tests that pinned the rendering pin
  the refusal. `tools/core_vocabulary_check.py` said the guard "checks a
  range" in the present tense.

The holes the flows have - minus zero, a `bool`, a `Decimal`, a `str` - are
shared by both types on purpose, so one rule settles all of them, and are
recorded on `PL-LLMN`, whose `touches` now reach `core/concentration.py`.

**The close-out review, 2026-10-05.** Three adversarial passes over the diff -
the type boundary and state, the domain, docs and display, and whether each
test fails with its check inverted. Folded in a second commit:

- `set_circuit_volume` wrote the volume before building the fraction it
  rewrites, so the one refusal that construction can make - for a fraction
  already held that no setter would have accepted - left the volume moved. It
  builds first now, under the circuit's name, and a test pins it.
- `BreathingCircuitState`, the record a rollback restores the circuit from,
  took a bare `float`. It checks the type when built, so `restore_state()`,
  which must not raise, is never handed one.
- Prose the change had made false: `advance()`'s docstring and a test's said
  the exact propagator cannot leave the range, which holds for the floor
  alone; `docs/MODEL.md` § "Displayed precision" still said guards made a
  negative impossible and that it is rendered; § "Concentrations" claimed the
  run-time refusal of a missing conversion everywhere, where it stands only
  where a concentration is held; `docs/ARCHITECTURE.md` left the types'
  constructors out of what raises `SimulationConfigurationError`; and
  `Percent`'s docstring stated a MAC's fitting in 0 to 100 as a rule, which
  nitrous oxide's 1.04 atm (Hornbein et al. 1982, PMID 7201254) falsifies on
  the roadmap, so it is written as the instance.
- The 100%-dial overshoot is given at its worst minute, 1.0000000002869551,
  beside the 24 h endpoint the design round quoted.

Filed rather than folded, under `parse-dont-validate`: `PL-7DJK`, how a
refusal on the display path is shown - unreachable from any supported setting,
but when the snapshot itself refuses, the halt is not shown at all, the
failure `PL-25KS` fixed for the frame - and `PL-5D1Z`, the pickle protocols 0
and 1 that load every checked type around its check.
