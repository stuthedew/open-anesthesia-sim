---
id: PL-HLTR
title: docs/ARCHITECTURE.md's startup diagram builds the system with AgentUptakeSystem.default(), but § 'Layering' and § 'Data flow' say for_agent() builds it from the data files; one is stale (copy editor structure read, 2026-11-05)
status: untriaged
feature: architecture-md-structure
added: 2026-11-05
---

**Problem.** docs/ARCHITECTURE.md's startup diagram builds the system with AgentUptakeSystem.default(), but § 'Layering' and § 'Data flow' say for_agent() builds it from the data files; one is stale (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/ARCHITECTURE.md at cfb15a4a, before the line edit):

- **Query, which constructor startup calls.** The file contradicts itself. The startup diagram in Data flow 159-174 builds the system with `AgentUptakeSystem.default()`. Layering 45-58 and Data flow 208-216 name `AgentUptakeSystem.for_agent()` as what builds the system from the data files. Which does startup call?
