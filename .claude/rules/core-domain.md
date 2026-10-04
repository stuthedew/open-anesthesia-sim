---
paths:
  - "/src/anesthesia_sim/core/**"
---

# The bar for `core/`: it should read like the domain

`CLAUDE.md` holds the simulator to the standard a top-tier specialist would
recognize. Under `core/` that standard has a concrete test, and it is this
one.

A clinician who knows uptake and distribution should recognize the physiology
in the code without a translation step — names that match the literature,
units carried in the identifier (`gas_volume_l`, `alveolar_ventilation_l_min`),
and the equation visible rather than buried under its own guards. Where a
guard, a facade, or a naming choice makes the model harder to see, the model
wins.

**"Would a reader who knows the domain guess this?"** is the test, and it
settles naming and boundary questions that "high quality" leaves open.

This is the bar for how the code reads. It does not relax anything in
`CLAUDE.md`'s safety-critical clinical-output standard, which decides what the
code must establish before it produces a number.

## The instance to read first

**The shape is `src/anesthesia_sim/core/tissue.py`.** Read it end-to-end before
adding or changing a compartment. It is the fullest instance of the pattern: a
frozen `TissueGroupState` carrying only what a step can change, and saying why
each parameter is excluded from it; a `__post_init__` refusing every field
through the named guards in `src/anesthesia_sim/core/validation.py`; properties
that carry the equation and cite the `docs/MODEL.md` section defining it; an
`advance()` whose docstring separates this compartment's own closed form from how
a run actually steps, and names both conditions it raises on.

`time_constant_s` is the clearest illustration of the bar above. It returns `inf`
for an unperfused tissue, and says that the step does not read it — the step uses
the reciprocal in `src/anesthesia_sim/core/governing_equations.py`, which states
the zero-flow case without a branch — because this is the form a reader of the
specification is looking for. A property kept for the reader rather than for the
arithmetic is what "reads like the domain" costs, and it is worth it.

## A quantity with a check of its own is a type, checked once

**Parse, don't validate** (project owner, 2026-10-04, `PL-M7QH`). A value whose
check is its own — a supported range, a whole count — enters `core/` through a
constructor that runs the check and returns a type nothing else produces, and
every signature and record field past that point takes the type. Holding one is
the proof, so nothing downstream checks the `float` again, and the equations
stay clear of guards, which is the bar above. The phrase is Alexis King's
("Parse, don't validate", 2019,
https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/). What it
replaces, a check at each way in, is what language-theoretic security calls
*shotgun parsing*: input checks mixed into and spread across the code that
processes the input (Momot, Bratus, Hallberg and Patterson, "The Seven Turrets
of Babel: A Taxonomy of LangSec Errors and How to Expunge Them", IEEE SecDev
2016,
https://www.iti.illinois.edu/credc/publications/seven-turrets-babel-taxonomy-langsec-errors-and-how-expunge-them).
`PL-HSFV` is that failure here: each compartment checked its flow's supported
range, and the settings record a run is built from was a way in that checked
none of them.

**The instance is `SimulationStep`, in
`src/anesthesia_sim/core/simulation_step.py`; read it before writing another.**
A `float` subclass whose `__new__` runs the range check; `require_simulation_step`
at each public entry point, refusing anything else with `TypeError`, because
Python enforces no annotation at run time; and `mypy --strict` refusing a bare
`float` where the type is expected. Two facts about Python are part of the
pattern rather than exceptions to it:

- A `NewType` is erased at run time, so it proves nothing about a range.
  `Fraction` and `Percent` in `src/anesthesia_sim/core/concentration.py` are
  NewTypes, and their ranges are still checked by hand wherever a value enters
  (`PL-4R3W`).
- Arithmetic on a `float` subclass returns a plain `float`. A derived value
  carries no proof, and is checked where it becomes a guarded parameter, by
  building the type there.

**Where it stops.** A frozen record whose constructor refuses its own fields is
already a parsed type for them — `tissue.py`'s `__post_init__` above — and a
relation between fields, such as tissue flows summing to cardiac output, belongs
to the record holding them rather than to any one quantity. What the principle
refuses is one quantity's own check made again by each record or function that
receives it. The shared sign-and-finiteness guards in `validation.py` stay with
each record that holds the field: the way in `PL-HSFV` found unguarded checked
the flows' sign and finiteness, and skipped their supported ranges. A record
found letting a bad sign through would be the evidence to widen this. `PL-51B7`
brings the flows, the case instant and the step count into line, in that order.
