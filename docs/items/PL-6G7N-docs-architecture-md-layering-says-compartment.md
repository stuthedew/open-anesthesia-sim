---
id: PL-6G7N
title: docs/ARCHITECTURE.md § 'Layering' says compartment defaults stay in core/ so a unit can be built bare, but § 'Where new code belongs' says a data-file value is a required argument with no default; new code cannot follow both (copy editor structure read, 2026-11-05)
status: untriaged
feature: architecture-md-structure
added: 2026-11-05
---

**Problem.** docs/ARCHITECTURE.md § 'Layering' says compartment defaults stay in core/ so a unit can be built bare, but § 'Where new code belongs' says a data-file value is a required argument with no default; new code cannot follow both (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/ARCHITECTURE.md at cfb15a4a, before the line edit):

- **Query, defaults in `core/`.** The file contradicts itself. Layering 45-58 says compartment defaults "are still written in `core/` so that a unit can be constructed bare", each pinned by a test. Where new code belongs 1171-1174 says a compartment takes a data-file value "as a required argument, with no default that restates it". Which rule applies to new code?
