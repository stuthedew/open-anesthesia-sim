---
id: PL-8W1Q
title: Every other frozen record in core/ that checks its fields in __post_init__ still restores from a pickle or a copy without running the check: a saved Keyframe with instant_s as a bare -50.0, a RunDefinition's slots and cache, BreathingCircuitState, SampledWindow, DeliverableFreshGasFlowRange, LiquidDensity and the parameter records all load unchecked, and nothing makes the next such record fail; the restore is also positional, so a record saved before a field reorder loads into the wrong fields (found at review of PL-S11T)
priority: P2
effort: M
status: done
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/core, tests/unit/test_record_restores.py, docs/ARCHITECTURE.md, docs/INTERFACE.md
added: 2026-10-27
closed: 2026-11-14
pr: 2166
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

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. `Keyframe`, `RunDefinition`, `SampledWindow`, `BreathingCircuitState` and `DeliverableFreshGasFlowRange` were frozen, checked records at `817a4d88`, and `CheckedQuantity.__reduce__` was the only restore guard. `LiquidDensity` came later (`c95177a6`).

**Built 2026-11-14 (step (c) of `PL-LHCL`).** The helper moved from
`core/governing_equations.py` to a new module, `core/checked_record.py`, as
`restore_through_checks`. It now passes the saved values to the constructor as
keyword arguments, so a record with a keyword-only field restores too, and it
refuses a state with the wrong number of values by name. The saved state still
holds the values in field order without their names, so the positional restore
that pass 1 of `PL-S11T`'s review named is not closed here; `PL-HXNL` carries
it. Nine more records
gained a `__setstate__` that calls it: `Keyframe` and `SampledWindow`
(`core/run_definition.py`), `BreathingCircuitState` and
`DeliverableFreshGasFlowRange` (`core/circuit.py`), `LiquidDensity`
(`core/liquid_agent.py`), and `AgentParameters`,
`BreathingCircuitParameters`, `ReferenceAdultParameters` and
`SupportedSchemaVersions` (`core/parameters.py`). With the two settings
records from `PL-S11T`, that is all eleven frozen dataclasses in `core/` that
check their fields in `__post_init__`.

`tests/unit/test_record_restores.py` holds
`test_every_checked_record_restores_through_its_checks`. It walks every module
in `core/` the way `tests/unit/test_record_writes.py` does, takes each frozen
dataclass with a `__post_init__`, hands an empty instance a state that is not
a list, and requires the helper's own refusal. The `__setstate__` that
`dataclass` writes gives a different error, so a new checked record without
the helper fails. A second test requires the walk to find the eleven named
records, so the walk cannot pass by finding nothing. The others replay the
escape: a `Keyframe` saved holding a bare -50.0 as `instant_s` is refused
through every pickle protocol, `copy.copy` and `copy.deepcopy`; a valid one
round-trips equal with its `CaseInstant` type kept; a `SampledWindow` saved
with three instants and two states is refused, which shows that a check across
two fields runs too.

**Failed first.** With the `src/` changes stashed and the new helper module
left in place, `uv run pytest -q -p no:randomly
tests/unit/test_record_restores.py` gave 10 failures:
`test_every_checked_record_restores_through_its_checks` with `AssertionError:
these checked records restore from a pickle or a copy without their checks`,
naming the nine records above, the eight Keyframe rebuilds with `Failed: DID
NOT RAISE TypeError`, and the `SampledWindow` test with `Failed: DID NOT RAISE
SimulationConfigurationError`.

**What this leaves.** Three kinds of record still restore without their
checks, and none is a frozen dataclass with `__post_init__`, so the Done-when
does not reach them. `RunDefinition` is a plain class with `__slots__`; a
restore sets its segments, its reached instant and its propagator cache
directly. `PatientCompartments` and `AgentUptakeSystem` are mutable
dataclasses whose writes `tests/unit/test_record_writes.py` already governs.
The Pydantic payloads in `core/parameters.py` restore their `__dict__`
without validation. Nothing in `src/` loads a pickle yet, so none is live; the
first saved-run loader's file format (plain data, rebuilt through each
constructor, as the triage above recommends) closes all three and the
positional restore together.

**Blind review, 2026-11-14.** Both passes named one finding: the helper could
not rebuild a record whose saved state is not its constructor's arguments, and
the walk would still have pushed such a record onto it. Three shapes do that: a
frozen dataclass without `slots=True`, whose state is a dict; a field with
`init=False`; and an `InitVar`. No current record has one. The helper now
refuses an `init=False` field by name, and
`test_every_checked_record_has_the_shape_that_restore_through_checks_reads`
requires each checked record to be slotted and its constructor to take exactly
its fields, so a misshapen record fails that test rather than every copy.

**Docs swept, 2026-11-14.** `docs/INTERFACE.md` § on how a saved record is
checked said that `Keyframe` did not yet check its values on load; it now says
which records do and points the rest at `PL-HXNL`. `docs/ARCHITECTURE.md` has
the new module's line. `docs/MODEL.md`, `README.md` and `.claude/` name neither
the old helper nor `__setstate__`, so nothing there changed.

**Second blind review, 2026-11-14,** on the final diff with `docs/INTERFACE.md`.
Both passes named one finding: the commit message, this item and
`docs/INTERFACE.md` said the helper restores "by field name", but the saved
state holds no names, so a reorder of two same-typed fields would still load
them swapped and pass every check. `docs/INTERFACE.md` and this item now say
the restore is positional, and the hazard moved into `PL-HXNL`'s title and
brief, where the saved-run file format closes it, as the triage above decided.
