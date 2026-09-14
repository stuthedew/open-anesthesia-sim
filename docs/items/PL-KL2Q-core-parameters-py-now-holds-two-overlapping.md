---
id: PL-KL2Q
title: core/parameters.py now holds two overlapping percent/fraction vocabularies - Pydantic's PositivePercent which validates but does not type-check, and concentration.py's Percent which type-checks but does not validate - and nothing says which a new field takes
priority: P2
effort: S
status: done
classes: refactor
feature: core-domain-language
milestone: v0.4.24
touches: src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/concentration.py
added: 2026-09-13
closed: 2026-09-14
pr: 561
verify: uv run pytest tests/unit/test_parameters.py && grep -qF 'Which vocabulary a new field in this file takes' src/anesthesia_sim/core/parameters.py
---

**Problem.** core/parameters.py now holds two overlapping percent/fraction vocabularies - Pydantic's PositivePercent which validates but does not type-check, and concentration.py's Percent which type-checks but does not validate - and nothing says which a new field takes

**Why it matters.** The two vocabularies do different halves of one job, and
the split is currently coherent by habit rather than by statement.
`_validate_positive_fraction` and `_validate_positive_percent` are Pydantic
`BeforeValidator`s exposed as `PositiveFraction` and `PositivePercent`: they
check a range at parse time and are plain `float` to `mypy`.
`concentration.py`'s `Fraction` and `Percent` are `NewType`s: they separate the
two conventions at every call site and check nothing at runtime. The payload
classes take the first, and `parse_agent_parameters` converts into the second
on the way out - `Percent(model.mac_percent)`.

Nothing says that is the rule, and one field already departs from it.
`MacAwakeReference` carries `fraction_of_mac: float` - neither validated nor
separated - so the validated-dataclass layer is not uniformly typed and a
reader cannot infer the convention from the file. A new field has four
plausible annotations, two of which validate nothing and two of which separate
nothing, and every displayed concentration in the application is computed from
these parameters.

**Decision needed.** What a new field in each layer takes, stated at the
fields. The reading the code already mostly follows - payload fields take the
validating `Positive*` alias, `AgentParameters` and its members take the
`concentration` `NewType` - is probably the answer, but adopting it means
deciding what to do with `MacAwakeReference.fraction_of_mac`, which is neither
and which `PL-BQ46` is separately asking about. The alternative worth pricing
before the rule is written down is removing the choice instead of documenting
it: `Annotated[Fraction, BeforeValidator(_validate_positive_fraction)]` is
available and would validate *and* separate in one annotation.

**Done when.** `core/parameters.py` states which vocabulary a new field takes
in each layer, at the fields rather than in a commit message, and every field
in the file either follows it or says why it does not.

**Decided 2026-09-14: the rule is the layer, not the quantity, and it is
written at the aliases.** The reading the code already mostly followed is
adopted and stated where a reader defining a new field will meet it — the
docstring under `PositiveFinite` / `PositiveFraction` / `PositivePercent` in
`core/parameters.py`.

- A `_...Payload` field takes a `Positive*` alias. The payload exists to refuse
  a bad file and is discarded immediately, so a type that marks a boundary buys
  nothing on a value about to be thrown away.
- A public dataclass field takes the `core/concentration.py` `NewType`. Those
  are what the rest of the application holds, so they are where a conversion
  can be missed. `parse_agent_parameters` and `parse_reference_adult_parameters`
  are the one crossing and wrap explicitly.
- A dimensionless quantity that is neither a concentration nor a ratio to MAC
  takes `PositiveFraction` and stays a bare `float` publicly —
  `perfusion_fraction` is the instance. A `NewType` per parameter is not the
  same thing as a `NewType` per boundary a wrong value can cross.

**The departure the brief named is gone rather than excused.**
`MacAwakeReference.fraction_of_mac` and `standard_deviation_fraction_of_mac`
were bare `float` — neither validated nor separated — and `PL-BQ46` gave them
`MacMultiple` in the same change. Every field in the file now follows the rule
above.

**The alternative was priced and refused.**
`Annotated[Fraction, BeforeValidator(_validate_positive_fraction)]` would
validate and separate in one annotation, and would delete the boundary
`_StrictPayload`'s own docstring calls deliberate: the payload would then carry
the public type, so nothing would distinguish a value that has been through
`parse_*` from one that has not. That is recorded in the docstring, so the next
reader meets the rejected option beside the rule.
