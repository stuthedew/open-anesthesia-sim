---
id: PL-LF0P
title: Scope v0.7.0, the schematic, in ROADMAP.md and freeze Gate 3 under it
priority: P2
effort: M
status: done
classes: planning
feature: schematic
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
