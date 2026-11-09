---
id: PL-HLTR
title: docs/ARCHITECTURE.md's startup diagram builds the system with AgentUptakeSystem.default(), but § 'Layering' and § 'Data flow' say for_agent() builds it from the data files; one is stale (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: done
classes: defect, docs
feature: architecture-md-structure
touches: docs/ARCHITECTURE.md
added: 2026-11-05
closed: 2026-11-09
pr: 2072
payoff: a contributor following the startup diagram lands on the constructor that startup actually calls
verify: ! grep -qF 'AgentUptakeSystem.default()' docs/ARCHITECTURE.md
reenters: PL-4FBP
---

**Problem.** docs/ARCHITECTURE.md's startup diagram builds the system with AgentUptakeSystem.default(), but § 'Layering' and § 'Data flow' say for_agent() builds it from the data files; one is stale (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/ARCHITECTURE.md at cfb15a4a, before the line edit):

- **Query, which constructor startup calls.** The file contradicts itself. The startup diagram in Data flow 159-174 builds the system with `AgentUptakeSystem.default()`. Layering 45-58 and Data flow 208-216 name `AgentUptakeSystem.for_agent()` as what builds the system from the data files. Which does startup call?

**Checked 2026-11-09:** `grep -n 'AgentUptakeSystem.default()' docs/ARCHITECTURE.md` still finds the startup diagram in § "Data flow". Startup does not call that method. `app/main.py` builds `BranchedCase(SimulationController())`. `SimulationController.__init__` in `app/controller.py` takes `agent_id="sevoflurane"` and calls `AgentUptakeSystem.for_agent(agent_id)`. `AgentUptakeSystem.default()` only returns `for_agent("sevoflurane")`, and its one caller is the field default of `SimulationState.uptake_system` in `core/simulation.py`. So § "Layering" and § "Data flow" are right, and the diagram is stale.

**Why it matters.** A contributor who follows the diagram to find where startup builds the system lands on a method that startup never calls. They may change it and see no effect.

**Done when.** The startup diagram names `AgentUptakeSystem.for_agent()`, the method that `SimulationController` calls.

**Generator check.** Instance of `PL-4FBP`'s fact, "The link between a document sentence and the tree fact it restates": the diagram names a code path that has moved, and no check holds a `docs/ARCHITECTURE.md` diagram to the code.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/ARCHITECTURE.md` already draws `AgentUptakeSystem.default()` in the startup diagram (row 149), while that tree's `app/controller.py` already calls `AgentUptakeSystem.for_agent(agent_id)`. So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.
