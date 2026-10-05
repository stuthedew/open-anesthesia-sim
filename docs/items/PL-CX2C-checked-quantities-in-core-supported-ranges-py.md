---
id: PL-CX2C
title: _CHECKED_QUANTITIES in core/supported_ranges.py leaves out Fraction and Percent, so a concentration handed where an instant or a step count belongs, or a step handed where a fraction belongs, is told to rebuild it as the type asked for rather than named as the swapped argument it is
priority: P2
effort: S
status: ready
classes: defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/core/supported_ranges.py, tests/unit/test_concentration.py, tests/unit/test_supported_ranges.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-05
payoff: a concentration handed where another quantity belongs, or another quantity where a concentration belongs, is named as the swapped argument it is, never told to rebuild into the wrong quantity under the right type
verify: grep -q 'def test_another_quantity_handed_in_as_a_concentration_is_refused_as_a_swapped_argument' tests/unit/test_concentration.py
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
`core/concentration.py` imports nothing from `core/` but its exceptions and,
since `PL-LLMN`, `core/checked_number.py`, and
`core/supported_ranges.py` already imports `core/simulation_step.py`, so a list
in either of the two would put an import between them that neither has now.
Found by `PL-4R3W`'s close-out review, outside that item's `touches`.

**Re-run 2026-10-05, at triage: it still holds.** On Python 3.14.7, against
`main` at `b67dace8`,

```bash
uv run python -c "from anesthesia_sim.core.supported_ranges import FreshGasFlow, require_case_instant, require_fresh_gas_flow; from anesthesia_sim.core.simulation_step import SimulationStep; from anesthesia_sim.core.concentration import Fraction, Percent, require_fraction, require_percent
for check, value in ((lambda v: require_case_instant('instant_s', v), Fraction(0.5)), (lambda v: require_fraction('alveolar partial_pressure_fraction', v), SimulationStep(0.05)), (lambda v: require_percent('delivered_concentration_percent', v), FreshGasFlow(2.0)), (require_fresh_gas_flow, Percent(2.0)), (require_fresh_gas_flow, SimulationStep(0.05))):
    try: check(value)
    except TypeError as e: print(str(e).split(': ')[1][:40])"
```

printed, for each, the rebuild advice - `build it as CaseInstant(...)`,
`Fraction(...)`, `Percent(...)`, and `FreshGasFlow(...)` twice - rather than
the quantity the value was built as.

**Why it matters.** The refusal is the only thing a caller reads about the
mistake, and its advice is what they do next. Told to rebuild, a caller who
handed a 0.5 fraction where an instant belongs builds `CaseInstant(0.5)` and
stores an instant of 0.5 s, which every later check admits: the refusal turns
a caught swap into a plausible wrong value one edit later. It stays `defect`
rather than `safety` because the swapped call itself is refused either way and
`mypy` refuses it in `src/`; what is wrong is the remedy offered.

**Overlap, settled here.** The third bullet's flow half - a step or an instant
handed as a flow - is `PL-848D`'s Done when, which brings `_require_built` and
`require_simulation_step` to the shared list. This item is the concentrations'
half: `Fraction` and `Percent` joining that list, and `require_fraction` and
`require_percent` reading it. `PL-979Z` reads the same list at the
constructors, so the three are best worked in one branch.

**Done when.** One list of every checked type - the three flows,
`SimulationStep`, `StepCount`, `CaseInstant`, `Fraction` and `Percent` - is
what every stored-value check reads to tell a swapped argument from a value
nobody built; where it lives without an import cycle is the implementer's call.
`require_case_instant` and `require_step_count` name a `Fraction` or a `Percent`
as the type it was built as and prescribe no rebuild, and so do the flows' and
the step's checks once `PL-848D` has them reading the list. `require_fraction`
and `require_percent` name every other checked quantity the same way, keeping
their convert-advice for each other. A bare `float` is still told to build the
type. A test in `tests/unit/test_concentration.py` named
`test_another_quantity_handed_in_as_a_concentration_is_refused_as_a_swapped_argument`
pins the concentrations' side, and the instant's and the count's existing
swapped-argument tests in `tests/unit/test_supported_ranges.py` gain a
`Fraction` and a `Percent`.
