---
paths:
  - "src/anesthesia_sim/core/**"
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
