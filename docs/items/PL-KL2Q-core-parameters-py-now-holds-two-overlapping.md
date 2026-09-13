---
id: PL-KL2Q
title: core/parameters.py now holds two overlapping percent/fraction vocabularies - Pydantic's PositivePercent which validates but does not type-check, and concentration.py's Percent which type-checks but does not validate - and nothing says which a new field takes
priority: P2
effort: S
status: needs-decision
classes: refactor
feature: core-domain-language
touches: src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/concentration.py
added: 2026-09-13
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
