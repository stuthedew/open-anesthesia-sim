---
id: PL-8W1Q
title: Every other frozen record in core/ that checks its fields in __post_init__ still restores from a pickle or a copy without running the check: a saved Keyframe with instant_s as a bare -50.0, a RunDefinition's slots and cache, BreathingCircuitState, SampledWindow, DeliverableFreshGasFlowRange, LiquidDensity and the parameter records all load unchecked, and nothing makes the next such record fail; the restore is also positional, so a record saved before a field reorder loads into the wrong fields (found at review of PL-S11T)
status: untriaged
feature: replay-findings
added: 2026-10-27
---

**Problem.** Every other frozen record in core/ that checks its fields in __post_init__ still restores from a pickle or a copy without running the check: a saved Keyframe with instant_s as a bare -50.0, a RunDefinition's slots and cache, BreathingCircuitState, SampledWindow, DeliverableFreshGasFlowRange, LiquidDensity and the parameter records all load unchecked, and nothing makes the next such record fail; the restore is also positional, so a record saved before a field reorder loads into the wrong fields (found at review of PL-S11T)

**Found by.** The two blind review passes on `PL-S11T`'s pull request, on
2026-10-27. `PL-S11T` closed the hole for `UptakeEquationSettings` and
`TissueGroupEquationSettings` only, through a private helper,
`_restore_through_checks` in `core/governing_equations.py`. Pass 1 loaded a
pickled run whose opening `Keyframe` held `instant_s = -50.0` as a bare
`float`, with no error. Nothing in `src/` loads a pickle yet, so this becomes
live with the first saved-run loader.

**Fix it by its shape.** `CLAUDE.md` asks for a second copy to be fixed by its
shape, so that the next instance fails. Two routes are open, and the choice
belongs to the design of the first saved-run loader. One route moves the helper
to a shared module, gives every checked record a `__setstate__` that calls it,
and adds a test that walks `core/` the way `tests/unit/test_record_writes.py`
does, so a new checked record without one fails. The other route saves a run as
plain data with field names and a format version, and rebuilds every record
through its constructor on load. The second route also closes the positional
restore that pass 1 named. It is the recommended one, because a pickle can call
any importable function, so no `__setstate__` makes a pickle safe to load from
an untrusted file.
