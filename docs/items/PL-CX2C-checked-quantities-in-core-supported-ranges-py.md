---
id: PL-CX2C
title: _CHECKED_QUANTITIES in core/supported_ranges.py leaves out Fraction and Percent, so a concentration handed where an instant or a step count belongs, or a step handed where a fraction belongs, is told to rebuild it as the type asked for rather than named as the swapped argument it is
status: untriaged
feature: parse-dont-validate
added: 2026-10-05
---

**Problem.** `core/supported_ranges.py`'s `_CHECKED_QUANTITIES` is the list
`require_case_instant` and `require_step_count` read to tell a swapped argument
from a value nobody built: one built as another checked quantity is named as
that, and not told to rebuild, because a rebuild would check and store the
wrong quantity under the right type. `PL-4R3W` made `Fraction` and `Percent`
checked types and did not add them, and their own `require_fraction` and
`require_percent` know only each other. Measured 2026-10-05:

- `require_case_instant("instant_s", Fraction(0.5))` answers "build it as
  CaseInstant(...) where the instant is chosen".
- `require_fraction("alveolar partial_pressure_fraction", SimulationStep(0.05))`
  answers "build it as Fraction(...) where it is computed".
- `require_percent("delivered_concentration_percent", FreshGasFlow(2.0))` and
  `require_fresh_gas_flow(Percent(2.0))` answer the same way, and the flows'
  `_require_built` names only the other two flows, so a step or an instant
  handed as a flow is told to rebuild too.

**Why it is not live.** `mypy --strict` refuses every one of these calls in
`src/`, so only a caller it does not read - a test, a notebook, a value typed
`Any` - reaches the message, and the call is refused either way. What is wrong
is the advice: the one fix it offers is the rebuild the pattern exists to
refuse (`.claude/rules/core-domain.md`).

**What a fix probably wants.** One list of every checked type, read by every
`require_*`, so the swapped-argument message is one rule rather than three
partial ones. Where the list lives is the design question:
`core/concentration.py` imports nothing from `core/` but its exceptions, and
`core/supported_ranges.py` already imports `core/simulation_step.py`, so a list
in either of the two would put an import between them that neither has now.
Found by `PL-4R3W`'s close-out review, outside that item's `touches`.
