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
