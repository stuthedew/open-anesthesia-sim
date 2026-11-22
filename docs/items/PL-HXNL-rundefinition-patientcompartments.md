---
id: PL-HXNL
title: RunDefinition, PatientCompartments, AgentUptakeSystem and the Pydantic payloads in core/parameters.py still restore from a pickle or a copy without their checks, because none is a frozen dataclass with __post_init__ and so PL-8W1Q's restore_through_checks and its walk do not reach them; and every checked record's saved state still holds its values by position, so a reorder of two same-typed fields would load them swapped; nothing in src/ loads a pickle yet (found building PL-8W1Q)
priority: P3
effort: M
status: ready
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/core, tests/unit/test_record_restores.py, docs/ARCHITECTURE.md
deferred-from: v0.7.0 - present at the freeze, deferred on a stated reason: no path in src/ restores these records from a pickle or a copy, so nothing a learner can reach goes through an unchecked restore, and PL-8W1Q, the frozen entry it follows, is complete for the restores that exist
added: 2026-11-14
payoff: A saved or copied run record cannot come back holding a value its constructor would refuse, or with two values swapped, once saved runs can be loaded.
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
0.01 g/mL. Both of the second pair of blind review passes on `PL-8W1Q` named it on
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
