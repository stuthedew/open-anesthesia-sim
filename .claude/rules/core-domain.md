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
