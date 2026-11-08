---
id: PL-LF0P
title: Scope v0.7.0, the schematic, in ROADMAP.md and freeze Gate 3 under it
priority: P2
effort: M
status: done
classes: planning
feature: schematic
milestone: v0.6.4
touches: ROADMAP.md, docs/items, docs/WORKING_NOTES.md
added: 2026-10-25
closed: 2026-10-25
pr: 1761
reason: v0.7.0 scoped in ROADMAP.md with Gate 3 frozen under it and its build items filed
payoff: The schematic has a scope, build items a session can pick, and a frozen Gate 3, so v0.7.0 can be worked instead of waiting on a section nobody wrote.
verify: grep -qF "## v0.7.0 - the schematic" ROADMAP.md && grep -qF "### Debt gate: the frozen list" ROADMAP.md
---

**Problem.** `ROADMAP.md` names v0.7.0, the schematic, on row 9 of § "The
timeline", but the milestone has no section. It has no goal, required scope,
definition of done or out-of-scope list, so no build item exists for it.
`bin/docket wave` reports the beat as "scope v0.7.0 — the schematic here,
which freezes its gate". Gate 3 freezes on the later of v0.7.0's scoping and
v0.6.0's ship, which was 2026-10-20, so it freezes on the day this section
lands. `PL-YRLM` also waits on this round to learn whether a release builds
planned-milestone item 28, agent cost.

**Why it matters.** Six entries that v0.6.0's gate could not place wait on a
section ahead: `PL-0S0V`, `PL-KZ99`, `PL-VJZK`, `PL-WZVZ`, `PL-5B1N` and
`PL-B396`. Until a section holds them, `bin/docket wave` reports the plan and
the project as disagreeing. The scoping round also found that item 27's own
description does not match Gas Man's Picture. The Workbook's Figure 2-1
(printed p. 11) draws every container at one width and fills it to a height
that is tension. So the Picture shows where the tension is, not where the
agent is, which is the lesson item 27 is written for.

**Done when.** `ROADMAP.md` carries `## v0.7.0 - the schematic` with its goal,
its frozen Gate 3 list, its required scope naming queue items, its definition
of done and its explicit out-of-scope list. The build items exist under
`feature: schematic`. `bin/docket wave` no longer asks for the scoping beat,
and `make check` is green.

**Generator check.** None: scoping a milestone is a beat of the cadence, and
nothing here produces findings of its own.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-YNFS`).** `ROADMAP.md`'s v0.7.0 section carried these three passages until then. The first ended the paragraph on what Gas Man's Picture shows: "Item 27" is planned-milestone item 27, the compartment schematic, and "so" is that Gas Man's Picture shows where the tension is and not where the agent is, which is the lesson item 27 was written for. The second ended the paragraph on containers drawn to scale, and "The measurement" is the model run that gave fat 493 L of gas equivalent and the 1 to 7 px widths. The third followed "Frozen 2026-10-25, the day this milestone was scoped" in the frozen list's first paragraph.

> Item 27 now says so.

> The measurement used `AgentUptakeSystem.for_agent` on the shipped parameter files, on 2026-10-25.

> v0.6.0 shipped on 2026-10-20. § "The debt gate" -> "The cadence" names two days, and the later of them is the scoping day.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-M3MV`).** `ROADMAP.md`'s § "Planned milestones" carried these paragraphs under item 27, "Schematic compartment view". In them, "this item" means item 27, and "above" and "below" point within that section as it then stood. Item 27 keeps its goal and a pointer to v0.7.0's scope.

> Add a schematic compartment view alongside the graph, after the interactive "Picture" of the Gas Man reference simulator. Gas Man draws the circuit, the alveoli and the blood and tissue groups as containers of one width. Each container is filled "to a height representing partial pressure or tension in that compartment" (Gas Man Workbook, Figure 2-1, printed p. 11). So its Picture shows where the tension is. Until 2026-10-25 this entry said that the containers were drawn to scale and filled with agent, which the Workbook does not say. This view adds what Gas Man leaves out: each container's amount, and a bar showing each compartment's share of the agent. **Scheduled in v0.7.0** (project owner, 2026-10-25, ratified, over containers drawn to scale and over Gas Man's Picture as it is). § "v0.7.0 - the schematic" has the scope.

> The view teaches something that the graph structurally cannot. The graph plots partial pressure, so fat shows near zero for hours while it holds a large and growing share of the agent. Measured in this model at a 1 MAC dial, fat holds a fifth of the stored agent at one hour and a third at three hours. Fat overtakes muscle only after about five to seven and a half hours (`PL-H5DV`). For that reason the compartment chart keeps its single linear axis and leaves this lesson to this view (project owner, 2026-09-23, ratified, over a reader-selected logarithmic scale on the chart, `PL-QYBW`). Where the drug *is*, in millilitres, and where the *tension* is are different questions. Confusing them is a standard novice error. The view needs per-compartment agent amounts exposed on the snapshot. The core already computes those amounts, and since `PL-KFTM` (2026-11-01) the snapshot carries them as one record per compartment.
