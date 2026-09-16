---
id: PL-J4NW
title: docs/ARCHITECTURE.md's 'Where new code belongs' routes every new display panel to run_view.py or simulation_view.py by asking whose it is, which is a fixed two-level layout the area model refuses - and .claude/rules/where-new-code-goes.md loads it on every src/ read
priority: P2
effort: S
status: done
classes: defect, docs
feature: interface-areas
touches: docs/ARCHITECTURE.md
added: 2026-09-16
closed: 2026-09-16
verify: python3 tools/doc_check.py check && grep -qF 'describes the fixed layout shipped today' docs/ARCHITECTURE.md
---

**Problem.** docs/ARCHITECTURE.md's 'Where new code belongs' routes every new display panel to run_view.py or simulation_view.py by asking whose it is, which is a fixed two-level layout the area model refuses - and .claude/rules/where-new-code-goes.md loads it on every src/ read

**Why it matters.** The routing is not passive documentation: it is loaded on
every `/src/**` read through `.claude/rules/where-new-code-goes.md`, so it is
the instruction a session actually follows when it adds a panel. It says a
panel about the chart both runs are drawn on - "an axis, a legend, a reference,
the time base, the compartment selection" - belongs to `SimulationView`, which
is a fixed container the area model dissolves. `.claude/rules/ui-areas.md`
loads on the same path and asks for the opposite: a view that does not assume
its size, its neighbours or that it is alone.

The two rules fire together and point different ways, which is the shape a
session cannot resolve on its own. `PL-9LNF` records the concrete cost already
paid: the chart time base is owned by a dropdown built into one plot's panel,
which is exactly what this routing prescribes.

**Done when.** `docs/ARCHITECTURE.md` § "Where new code belongs" routes a
display surface by what it *is* rather than by which container currently holds
it, or states its own condition - that it describes today's fixed layout and is
superseded when the area system lands. `PL-TH35` owns adding the "a new editor"
route; this item is about the sentence that is there now.

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** Surfaced 2026-09-16 by the area-model audit's completeness critic, after the main sweep had closed - which is the critic earning its place rather than a defect in the sweep.
