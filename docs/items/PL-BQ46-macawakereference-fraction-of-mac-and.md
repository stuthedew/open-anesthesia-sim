---
id: PL-BQ46
title: MacAwakeReference.fraction_of_mac and formatting.mac_multiple are a third and fourth dimensionless convention beside Fraction, and neither is distinguished from a concentration fraction at the type level
priority: P2
effort: S
status: needs-decision
classes: refactor
feature: core-domain-language
touches: src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/app/formatting.py
added: 2026-09-13
---

**Problem.** MacAwakeReference.fraction_of_mac and formatting.mac_multiple are a third and fourth dimensionless convention beside Fraction, and neither is distinguished from a concentration fraction at the type level

**Why it matters.** `core/concentration.py` exists because one quantity
arrived in two forms and every crossing between them was a place a correct
number could acquire the wrong meaning (`PL-WVSK`). Two more dimensionless
quantities cross the same boundaries and neither is in it:

- `MacAwakeReference.fraction_of_mac` and
  `standard_deviation_fraction_of_mac` are bare `float`, and are ratios to the
  agent's own MAC. The class docstring is explicit that the fraction is *of
  MAC* and never of an atmosphere.
- `formatting.mac_multiple()` returns a bare `float` - the same ratio with no
  upper bound, since a compartment may sit above 1 MAC.

So four dimensionless conventions are in play - a fraction of an atmosphere, a
percent of one, a ratio to MAC and a multiple of MAC - and `mypy` separates
only the first two. The first and third are the dangerous pair, because they
are small numbers of the same magnitude: sevoflurane at 1 MAC is
`Fraction(0.02)` against a MAC-awake `fraction_of_mac` near 0.34, and either
passed where the other is wanted type-checks and yields a plausible reading.
A MAC-awake band drawn at 0.02 of MAC rather than 0.34 is a chart reference in
the wrong place with nothing on the screen saying so.

**Decision needed.** Whether a MAC-relative type earns its place, and where it
lives. `concentration.py`'s own docstring bounds what any answer may claim:
arithmetic erases a `NewType`, so it guards a boundary and nothing else - and
this quantity does cross boundaries, from `parse_agent_parameters` through the
snapshot into `formatting` and the chart. Against that, the module is named for
concentration and a ratio to MAC is not one, so a third type either widens its
subject or needs a home of its own. The cheap wrong answer to rule out
explicitly is annotating `MacAwakeReference`'s two fields with the existing
`Fraction`, which would assert the opposite of what the docstring says.

**Done when.** Either a MAC-relative type exists and every boundary carrying
one is annotated with it, or the decision not to add one is recorded where the
next reader of `MacAwakeReference.fraction_of_mac` and `mac_multiple()` will
meet it, saying what `mypy` does and does not separate here.
