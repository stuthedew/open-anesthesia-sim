---
id: PL-HXNL
title: RunDefinition, PatientCompartments, AgentUptakeSystem and the Pydantic payloads in core/parameters.py still restore from a pickle or a copy without their checks, because none is a frozen dataclass with __post_init__ and so PL-8W1Q's restore_through_checks and its walk do not reach them; nothing in src/ loads a pickle yet (found building PL-8W1Q)
status: untriaged
feature: replay-findings
added: 2026-11-14
---

**Problem.** RunDefinition, PatientCompartments, AgentUptakeSystem and the Pydantic payloads in core/parameters.py still restore from a pickle or a copy without their checks, because none is a frozen dataclass with __post_init__ and so PL-8W1Q's restore_through_checks and its walk do not reach them; nothing in src/ loads a pickle yet (found building PL-8W1Q)

**Found by.** Building `PL-8W1Q` on 2026-11-14. Its § "What this leaves" has
the detail. `RunDefinition` is a plain class with `__slots__`, so a restore
sets its segments, its reached instant and its propagator cache directly.
`PatientCompartments` and `AgentUptakeSystem` are mutable dataclasses. The
Pydantic payloads restore their `__dict__` without validation. `PL-8W1Q`'s
triage recommends that the first saved-run loader (planned milestone item 9 in
`ROADMAP.md`) save a run as plain data with field names and rebuild each record
through its constructor, which would close all of these together.
