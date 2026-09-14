---
id: PL-BQ46
title: MacAwakeReference.fraction_of_mac and formatting.mac_multiple are a third and fourth dimensionless convention beside Fraction, and neither is distinguished from a concentration fraction at the type level
priority: P2
effort: S
status: done
classes: refactor
feature: core-domain-language
touches: src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/app/formatting.py, tests/unit/test_formatting.py
added: 2026-09-13
closed: 2026-09-14
verify: uv run pytest tests/unit/test_formatting.py && grep -q 'def test_a_concentration_fraction_reaching_the_mac_awake_band_is_refused_by_mypy_alone' tests/unit/test_formatting.py
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

**Decided 2026-09-14: a MAC-relative type earns its place, and it lives in
`core/concentration.py`.** `MacMultiple` is a `NewType` over `float` beside
`Fraction` and `Percent`.

**Why it earns its place.** The hazard the brief names is reachable rather than
theoretical, and the test added with this item is the demonstration.
Sevoflurane's MAC-awake band is 0.34 ± 0.05 MAC against a MAC of 2.0%, so it is
drawn at 0.58–0.78% — the decrement a falling alveolar trace has to cross for
arousal. Pass a *circuit fraction* at the vaporizer's own 8% maximum into the
same call and every runtime guard accepts it, because 0.08 − 0.05 is still
positive: the band is then drawn at 0.06–0.26%, below the awakening
concentration, where a trace crosses it late or never. Nothing on the screen
says so, and `CLAUDE.md` treats a clinical reference in the wrong place as a
safety failure rather than a presentation one. `tools/ignore_check.py` reports
the two new directives live, so the refusal is real and not asserted.

**Why `core/concentration.py` and not a module of its own.** `docs/MODEL.md`
§ "Concentrations" — the section that module implements — is where the MAC
multiple is *defined*, as $`100F/\mathrm{MAC}_\%`$, a rescaling of the same
$`F`$ by one per-agent constant. A type for it therefore widens no subject; it
completes one. `PL-6KNM` settles the module's name on the same ground.

**One type, not two.** A ratio to MAC and a multiple of MAC are one kind
differing only in range, so a second `NewType` for the bounded case would
reintroduce the multiplicity this one removes. The bound that matters —
`MacAwakeReference` staying below 1 MAC — is held by `_MacAwakePayload`'s
validator, which checks values; a `NewType` marks boundaries and checks
nothing.

**Annotated at the boundaries, not at the locals**, because the module docstring
already measured that arithmetic erases a `NewType`: `MacAwakeReference`'s two
fields, `parse_agent_parameters`' construction of them, `mac_multiple()`'s
return, and the `fraction_of_mac` / `standard_deviation_fraction_of_mac`
parameters of `mac_awake_band_percent` and `format_mac_awake_reference`.
`mac_axis_ticks`' `span_mac` and `step_mac` are locals inside one function and
are left alone.

**Left, and filed.** `mac_percent` is a `Percent` in two `app/formatting.py`
signatures and a bare `float` in five others — one parameter, two types, in one
module. It is not a MAC-relative value, so it is outside what this item decides:
`PL-W3Q5`.
