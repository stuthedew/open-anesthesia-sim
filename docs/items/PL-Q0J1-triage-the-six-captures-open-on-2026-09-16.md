---
id: PL-Q0J1
title: Triage the six captures open on 2026-09-16, second pass
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
touches: docs/items
added: 2026-09-16
closed: 2026-09-16
not-delegable: a triage pass is proven by the store's state at the moment it ran, and that state moves - captures arrive untriaged by design - so no command run afterwards separates 'the pass happened' from 'nothing has been captured since'. `bin/docket check`, already on `make check`, is the standing proof that what the pass wrote is valid (same argument as PL-0C6W, PL-2B7B, PL-Q2PX and PL-LYX2)
---

**Problem.** Triage the six captures open on 2026-09-16, second pass

**Why it matters.** `PL-0C6W` cleared the fourteen open that morning; six more
arrived across the day, from four sessions. Untriaged items are invisible to
`bin/docket next` - they carry no band, so nothing ranks them - which means a
finding sits in the queue looking recorded while being unreachable by every
session that asks what to do next.

**What was decided, and why.**

| item | landed on | reason |
| --- | --- | --- |
| `PL-2M4X` | `P3 · S · ready`, `release-roadmap-seam` | metadata repair on `PL-J45M`, seated at `PL-J45M`'s own band - the skill's rule is that a wrong `verify:` is repaired as its item is started, so ahead of that it buys nothing |
| `PL-85NT` | `dropped` | superseded by `PL-99YZ` on this item's own recommendation; its measurements are cited into `PL-99YZ` rather than repeated |
| `PL-L4KX` | `P2 · S · ready`, `delegation` | the only `P2` of the six: `bin/docket verify --self` REJECTs any close-out that drops an item, and this pass drops one, so the defect fires today |
| `PL-M3YJ` | `P3 · S · ready`, `dev-tooling` | a suppression that outlives its module is reported by nothing; cost of the flag is zero while `pyqtgraph` is the only override left |
| `PL-PGZF` | `P3 · M · ready`, `chart-readout` | kept separate from `PL-CNCF` rather than folded: different functions in different modules, and `PL-CNCF` carries `docs/MODEL.md` where this carries neither |
| `PL-SYG4` | `P3 · M · needs-decision`, `release-process` | three digest wordings differ in what they commit the project to, and one of them writes a claim on a scoped section's name into a digest line - the owner's call |

**Banding, against the standing advisory.** `docket check` reports 135
startable `P2` items against a limit of 12 and asks for demotion, so a `P2`
here needs defending rather than assuming. Five of the six are `P3`. The
exception, `PL-L4KX`, is `CLAUDE.md`'s second compounding-friction test read
literally: a refusal fired routinely on correct work, which trains a reader to
skim the block where a real protected-path failure is printed.

**Done when.** `bin/docket check` reports zero untriaged items and zero errors,
every one of the six carries the fields `docket check` requires at its status,
and each `ready` item names a `verify:` command that was run and watched fail
for the right reason before it was written down.
