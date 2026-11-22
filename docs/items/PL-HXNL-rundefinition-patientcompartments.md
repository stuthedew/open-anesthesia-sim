---
id: PL-HXNL
title: RunDefinition, PatientCompartments, AgentUptakeSystem and the Pydantic payloads in core/parameters.py still restore from a pickle or a copy without their checks, because none is a frozen dataclass with __post_init__ and so PL-8W1Q's restore_through_checks and its walk do not reach them; and every checked record's saved state still holds its values by position, so a reorder of two same-typed fields would load them swapped; nothing in src/ loads a pickle yet (found building PL-8W1Q)
priority: P3
effort: M
status: done
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/core, tests/unit, docs/ARCHITECTURE.md, docs/INTERFACE.md
deferred-from: v0.7.0 - present at the freeze, deferred on a stated reason: no path in src/ restores these records from a pickle or a copy, so nothing a learner can reach goes through an unchecked restore, and PL-8W1Q, the frozen entry it follows, is complete for the restores that exist
added: 2026-11-14
closed: 2026-11-22
pr: 2242
payoff: A saved or copied run record cannot come back holding a value its constructor would refuse, or with two values swapped, once saved runs can be loaded.
tests: tests/unit/test_record_restores.py::test_every_class_in_core_restores_by_name_through_its_checks, tests/unit/test_record_restores.py::test_a_record_saved_before_two_fields_changed_places_loads_each_value_into_its_own_field, tests/unit/test_record_restores.py::test_a_saved_patient_whose_fractions_do_not_sum_to_one_is_refused, tests/unit/test_record_restores.py::test_a_saved_system_whose_accounting_does_not_balance_is_refused, tests/unit/test_record_restores.py::test_a_saved_definition_that_goes_back_in_time_is_refused, tests/unit/test_record_restores.py::test_a_saved_payload_whose_fractions_do_not_sum_to_one_is_refused, tests/unit/test_record_restores.py::test_a_shallow_copy_of_a_run_is_refused
---

**Problem.** RunDefinition, PatientCompartments, AgentUptakeSystem and the Pydantic payloads in core/parameters.py still restore from a pickle or a copy without their checks, because none is a frozen dataclass with __post_init__ and so PL-8W1Q's restore_through_checks and its walk do not reach them; and every checked record's saved state still holds its values by position, so a reorder of two same-typed fields would load them swapped; nothing in src/ loads a pickle yet (found building PL-8W1Q)

**Found by.** Building `PL-8W1Q` on 2026-11-14. Its § "What this leaves" has
the detail. `RunDefinition` is a plain class with `__slots__`, so a restore
sets its segments, its reached instant and its propagator cache directly.
`PatientCompartments` and `AgentUptakeSystem` are mutable dataclasses. The
Pydantic payloads restore their `__dict__` without validation. `PL-8W1Q`'s
triage recommends that the first saved-run loader (planned milestone item 9 in
`ROADMAP.md`) save a run as plain data with field names and rebuild each record
through its constructor, which would close all of these together.

**The positional restore goes with them.** Every checked record's saved state
holds its field values in field order, without their names, and
`restore_through_checks` pairs them with today's field names. If two fields of
the same type are reordered, a record saved before the change loads with the
values swapped and passes every check. `LiquidDensity`'s density and its
standard deviation are one such pair: swapped, the density would load as about
0.0008 g/mL (sevoflurane's standard deviation; corrected 2026-11-22 from "about 0.01"). Both of the second pair of blind review passes on `PL-8W1Q` named it on
2026-11-14. The
same plain-data format closes it; a `__getstate__` returning the values by
name would close it sooner for in-process copies.

**Checked 2026-11-22**, at `d4e8200c`. `grep -rn 'def __setstate__' src/anesthesia_sim/core`
lists `core/run_definition.py:69`, which belongs to the stretch record above
`RunDefinition`, and none for `RunDefinition` itself (a plain class with
`__slots__ = ("_reached_s", "_segments")` at line 98), `PatientCompartments`
(`core/patient.py:53`, `@dataclass(slots=True)`) or `AgentUptakeSystem`
(`core/uptake_system.py:125`, the same). The docstring of
`restore_through_checks` in `core/checked_record.py` (lines 51 to 55) still
says that the saved state holds values in field order without their names.
`grep -rn 'pickle\.' src` finds no loader. So both gaps are present, and
nothing in the simulator reaches them yet.

**Why it matters.** A record restored without its checks can carry a value its
constructor would refuse, and a positional restore after a field reorder can
swap two values silently, for example a liquid density and its standard
deviation. Either would reach a learner as a plausible-looking number once a
saved run can be loaded. Today no path loads or copies these records, so no
learner can see such a value.

**Done when.** Every record in `core/` that checks its fields, the three named
here and the parameter payloads included, runs those checks when a pickle or a
copy rebuilds it, and a saved record restores its values by field name. A test
shows a restored record refusing an invalid value, and a test shows that a
reorder of two fields of one type does not swap them on restore.

**Generator check.** The fact is which values a record may hold once it is
rebuilt, which `PL-LHCL` (numbers whose valid range nothing checks) states in
its `misread:`. That head is still open, and `PL-8W1Q` is one of its members.
This item was filed by the pull request that closed `PL-8W1Q`, as that item's
stated remainder, so it is not a fix that failed to hold, and no `reenters:`
is recorded.

**What was built (2026-11-22).** Every class in `core/` other than an
exception or a checked quantity now saves its state as a dict from each field
name to its value, and refuses on load any other shape, a list in field order
included, through `require_state_by_name` in `core/checked_record.py`.

1. A dataclass whose constructor takes every field carries the decorator
   `restored_through_checks`. Its `__setstate__` runs the record's own
   `__init__` on the empty object with the values by name, so `__post_init__`
   and any `__setattr__` guard run as they do at construction. That covers
   the 13 checked frozen records, the unchecked frozen records, the mutable
   compartments and `PatientCompartments`. The decorator refuses at import a
   dataclass whose constructor does not take exactly its fields.
2. `RunDefinition` replays its saved stretches through its own `advance_to`
   and `record_change`, and refuses a saved list that the replay does not
   rebuild exactly.
3. `StoredStates` reopens from its first saved state and `append`s each later
   one, so every state passes `require_canonical_state` again on a pickle.
   Its `__copy__` still copies the arrays, which only its own checked methods
   ever filled, because a branch opens with a copy and a replay of a long run
   would slow that.
4. `AgentUptakeSystem` does not run its constructor, which would anchor the
   accounting again and hide agent the saved parts gained or lost. It writes
   its four parts and then checks the dial against the input ceiling and the
   accounting identity.
5. `SimulationState` runs its constructor with the saved stored states as the
   opening record, so it is checked as a branch is.
6. `AgentSimulationValidator` writes each total and term through its
   `__setattr__`, because the constructor does not take the two terms.
7. `_StrictPayload` validates a pickled payload's fields again, and its
   `__copy__` and `__deepcopy__` build the copy through `model_validate`,
   because Pydantic's own copies skip both the validators and `__setstate__`.

`tests/unit/test_record_restores.py` walks `core/` and holds every class to
both halves.

**New problems fixed on the way.** `SimulationState` accepted any object as
its uptake system, and `AgentUptakeSystem` any object as one of its four parts,
and each failed later on a missing attribute. Each `__setattr__` now refuses an
object of the wrong type.

**Blind review, two passes.** Pass 1 named a mid-run circuit volume change
that leaves the system off its stored state, so a copy of that run is now
refused (optional, filed as `PL-DQWL`), and the missing part type check
(optional, fixed). Pass 2 named the same part type check (optional, fixed,
repeat) and a shallow copy of a run (should-fix, fixed). The copy got a record
of its own through its constructor but shared the original's system, so
stepping one moved the system under the other: the original's next step
stored an alveolar fraction of 0.00272 as its 6 s state, where a fresh run
gives 0.00113. `SimulationState.__copy__` now refuses, and names
`copy.deepcopy`.

**The regression tests fail against the code before the fix.** A scratch
script run on `origin/main` at `d2f987d4` loaded, through `pickle`, each of the
values the new tests refuse. It printed "patient with fractions 0.42 loaded",
"system with unbalanced accounting loaded: False", "definition reached 60 with
last stretch at 90 loaded" and "payload with muscle fraction 0.5 loaded". It
also printed `LiquidDensity state: [1.5203, 0.0008, 20.0]`, the positional
form. The new test file imports `restored_through_checks`, which does not exist
there, so the script stands in for it.

**Docs checked.** `docs/ARCHITECTURE.md` (the line for `checked_record.py`),
`docs/INTERFACE.md` (the note for developers that said the run definition, the
patient and the payloads did not check their values on load), and the
docstrings in `core/` and `tests/unit/` that said a copy or a pickle restores a
slotted dataclass one field at a time. `docs/MODEL.md`, `docs/VERIFICATION.md`,
`docs/PARAMETERS.md` and `README.md` name no pickle or copy.
