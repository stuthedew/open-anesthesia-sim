---
id: PL-93B3
title: Keep a reader's preferences, the agent price and the agent cost unit first, in a preferences file of their own, separate from the Workspaces
priority: P1
effort: M
status: ready
classes: feature
feature: preferences-store
touches: src/anesthesia_sim, tests/unit, docs/ARCHITECTURE.md
added: 2026-10-25
payoff: a reader's agent price and cost unit persist across a restart in a store of their own, separate from the Workspaces
verify: grep -rq 'def test_a_preference_survives_a_restart' tests
---

**Where this came from.** `PL-LF0P` scoped v0.7.0 on 2026-10-25 with agent
cost inside it. `PL-MQHN` decided that preferences and Workspaces are separate
stores, so that Blender's Save, Revert and Load Factory Preferences workflow
can be added later. Nothing in `src/` stores a preference yet.

**Problem.** The agent price (`PL-1P15`) and the agent cost View's unit
(`PL-B396`) belong to the reader, not to a layout. Folding them into a
Workspace file is what `PL-MQHN` refused.

**What to build.** A versioned, validated preferences file of its own, read
and written through one module, beside the Workspace store and not inside it.
It holds the agent price per agent with its currency and date, and the agent
cost View's unit. A first run with no file uses the shipped defaults. A file
with an unsupported schema version is refused with a clear message, the way
`PL-SSQW` decided for the Workspace file.

**Why it matters.** Without a store of its own, the price either lives in a
Workspace, which `PL-MQHN` refused, or is lost at every restart, which makes a
reader-set price useless for comparing a case against their own institution.

**Done when.** The price and the unit persist across a restart, a missing or
unreadable file fails safely, and `docs/ARCHITECTURE.md` describes the store.
