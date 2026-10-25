---
id: PL-PR1W
title: Place the compartment schematic beside the concentration chart in one shipped Workspace
priority: P2
effort: S
status: blocked
classes: feature
feature: schematic
touches: src/anesthesia_sim/data/workspaces, tests/unit
blocked-by: PL-RNYV
added: 2026-10-25
payoff: a learner meets the schematic beside the concentration chart without building that layout first
verify: grep -rq 'compartment_schematic' src/anesthesia_sim/data/workspaces
---

**Where this came from.** `PL-LF0P` scoped v0.7.0, the schematic, on 2026-10-25. The project owner chose containers that fill to tension, labelled with their amounts, plus a bar showing each compartment's share of the agent (project owner, 2026-10-25, ratified, over containers drawn to scale and over Gas Man's Picture as it is). `ROADMAP.md` § "v0.7.0 - the schematic" has the reasoning and the measurements behind it.

**Problem.** A new View that no shipped Workspace places is one a learner has
to find and place before they can use it.

**What to build.** One shipped Workspace under
`src/anesthesia_sim/data/workspaces/` places the schematic beside the
concentration chart, so a learner meets tension over time and where the agent
is now side by side. Which Workspace is a placeholder decision.

**Why it matters.** `ROADMAP.md` § "v0.7.0 - the schematic" asks that a
learner meet tension over time and where the agent is now side by side, and a
shipped placement is what makes that the first thing they see.

**Done when.** The shipped Workspace JSON places the schematic, it loads
through the shipped-Workspace reader, and its tests pass.
