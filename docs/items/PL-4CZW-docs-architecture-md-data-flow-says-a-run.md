---
id: PL-4CZW
title: docs/ARCHITECTURE.md § 'Data flow' says a run forked onto the supported run length is treated as stopped there, but the branch chapter says a fork there is refused; one is stale (copy editor structure read, 2026-11-05)
status: untriaged
feature: architecture-md-structure
added: 2026-11-05
---

**Problem.** docs/ARCHITECTURE.md § 'Data flow' says a run forked onto the supported run length is treated as stopped there, but the branch chapter says a fork there is refused; one is stale (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/ARCHITECTURE.md at cfb15a4a, before the line edit):

- **Query, a branch at the supported run length.** The file contradicts itself. Data flow 409-422 says "a run forked or reset onto that step is also treated as stopped there". Branch 572-589 and 590-601 say a fork at the supported run length is refused ("`_resume_point` rejects a fork there for every method"). Can a branch open there?
