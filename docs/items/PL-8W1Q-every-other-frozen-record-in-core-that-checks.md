---
id: PL-8W1Q
title: Every other frozen record in core/ that checks its fields in __post_init__ still restores from a pickle or a copy without running the check: a saved Keyframe with instant_s as a bare -50.0, a RunDefinition's slots and cache, BreathingCircuitState, SampledWindow, DeliverableFreshGasFlowRange, LiquidDensity and the parameter records all load unchecked, and nothing makes the next such record fail; the restore is also positional, so a record saved before a field reorder loads into the wrong fields (found at review of PL-S11T)
priority: P2
effort: M
status: ready
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/core, tests/unit/test_record_restores.py
deferred-from: v0.7.0 - filed after the gate froze; nothing in src/ loads a pickle yet, so no run reaches the unchecked restore
added: 2026-10-27
payoff: a record restored by a pickle or a copy is checked as the constructor checks it, and the next checked record cannot skip that
verify: grep -q 'def test_every_checked_record_restores_through_its_checks' tests/unit/test_record_restores.py
reenters: PL-S11T
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

**Why it matters.** Every one of these records refuses a bad value when it is
built, and the rest of `core/` relies on that. A restore that skips the check
produces a record that the type says was checked and that was not. Nothing in
`src/` loads a pickle today, so no learner meets this yet. But the tree
already treats a restore as a way in that must be guarded:
`CheckedQuantity.__reduce__`, `PL-N7MM`'s write guards and `PL-S11T`'s
`_restore_through_checks` each do so for their own types. So the rule is
applied in some records and not in others, and nothing makes the next checked
record follow it.

**Triaged 2026-10-27: take the first route now, and leave the file format to
the loader.** The two routes do not exclude each other. The `__setstate__`
route closes the gap for every in-process restore, makes the rule uniform,
and adds the test that makes the next record fail. Nothing is stored yet, so
nothing downstream would have to be redone. The plain-data route is the
recommendation for the first saved-run loader's file format, because a pickle
can call any importable function, and no `__setstate__` makes a pickle from an
untrusted file safe. That choice belongs to the loader, which is planned
milestone item 9 in `ROADMAP.md` and not yet scoped. The positional restore
that pass 1 named goes with it.

**Done when.** The helper `_restore_through_checks` lives in a shared module
in `core/`, and every frozen record in `core/` that checks its fields in
`__post_init__` restores through it, so a pickle or a copy runs the same
checks as the constructor. `tests/unit/test_record_restores.py` has
`test_every_checked_record_restores_through_its_checks`, which walks `core/`
the way `tests/unit/test_record_writes.py` does and fails for a checked record
that restores without its checks, and a test that loads a pickled `Keyframe`
whose `instant_s` is a bare -50.0 and expects the refusal.

**Generator check.** A re-entry of `PL-S11T`, the same mechanism at the
sibling records its fix left out. `PL-5D1Z` met it first, for the flow values.
The fact misread is whether a record rebuilt by a pickle or a copy ran its
constructor's checks. It is an instance of `PL-ZGYX`'s family fact, which
other re-entries already name.
