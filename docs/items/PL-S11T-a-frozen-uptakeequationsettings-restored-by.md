---
id: PL-S11T
title: A frozen `UptakeEquationSettings` restored by unpickling is rebuilt through `__setstate__`, so its `__post_init__` never runs: a saved record whose state holds cardiac output as a bare 1000.0 and fresh gas flow as NaN loads with no error, and `RunDefinition` accepts it and advances, although `PL-5D1Z` closed the same hole for the flow values themselves
priority: P2
effort: S
status: ready
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/core/governing_equations.py, tests/unit/test_governing_equations.py, docs/MODEL.md
added: 2026-10-25
payoff: holding a settings record stays proof that its flows are in range, even for one read back from a saved file
verify: grep -q 'def test_an_unpickled_settings_record_is_rebuilt_through_its_checks' tests/unit/test_governing_equations.py
---

**Problem.** `UptakeEquationSettings` and `TissueGroupEquationSettings` are `@dataclass(frozen=True, slots=True)` (`core/governing_equations.py`). Unpickling restores them with `__newobj__` and the generated `__setstate__`, which bypasses `__post_init__` (`governing_equations.py`). `CheckedQuantity.__reduce__` (`core/checked_number.py`) protects a flow that is pickled as its checked type. It does not protect a field whose stored state holds a bare float, which is the form every record pickled before #1350 has. `RunDefinition.__init__` (`core/run_definition.py`) does not re-check the record.

**Why it matters.** Holding an `UptakeEquationSettings` is meant to prove its flows are in range and its tissue flows sum to the cardiac output. Reproduced: a restored record with cardiac output 1000.0 (tissue flows still summing to 5) and fresh gas flow NaN loaded. `RunDefinition` accepted it, and a record with only the cardiac output forged advanced 10 s and returned a state with no error. Nothing in `src/` loads a pickle today, so this becomes live with the first saved-run loader. A `__reduce__` that rebuilds through the constructor, or a `__setstate__` that re-runs `__post_init__`, closes it at every protocol. It is filed P2 `defect` and not as a safety
item, as `PL-5D1Z` classed the sibling hole for the flow values, because
nothing in `src/` loads a pickle.

**Done when.** An `UptakeEquationSettings` or `TissueGroupEquationSettings` restored by unpickling, at any protocol, runs the same checks as its constructor, so a forged state with an out-of-range cardiac output or a NaN fresh gas flow is refused on load. `tests/unit/test_governing_equations.py` has `test_an_unpickled_settings_record_is_rebuilt_through_its_checks`.

**Found by.** `PL-TBQS` reviewer replay on #1350, r02 F1 and r04 F1 (the record half; their flow half and `PL-ZWXD`'s entry were fixed by `PL-5D1Z`). Checked against main 2026-10-25, reproduced with `scripts/B_pickle.py`.
