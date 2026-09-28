---
id: PL-KRGY
title: ROADMAP.md and docs/ARCHITECTURE.md's product placement in workflow_paths sets aside 90 and 40 items that pair them only with apparatus paths - 14 open - because both documents also carry apparatus facts, so the deliberate absence written when it cost four items now costs the crossing set most of its members
priority: P3
effort: M
status: needs-decision
classes: docs, infra
feature: parallel-sessions
touches: docket.toml, docs/ARCHITECTURE.md, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-28 triage pass
added: 2026-09-27
---

**Problem.** ROADMAP.md and docs/ARCHITECTURE.md's product placement in workflow_paths sets aside 90 and 40 items that pair them only with apparatus paths - 14 open - because both documents also carry apparatus facts, so the deliberate absence written when it cost four items now costs the crossing set most of its members

**Evidence, 2026-09-27, measured through `Item.lane` against the store as
`#1199` leaves the list** (the count `PL-8ZGY`'s design round ran; its script
is not in the tree). `docket.toml`'s `workflow_paths` records `ROADMAP.md`
and `docs/ARCHITECTURE.md` as deliberately absent, and the paragraph beside
them says four items reaching both a tool and the roadmap were set aside as a
result, "which is the right answer". The count today:

| Path | Items declaring it | Paired only with apparatus paths | Open among those |
| --- | --- | --- | --- |
| `ROADMAP.md` | 244 | 90 | `PL-B396`, `PL-DHJ7`, `PL-GL95`, `PL-KKRP`, `PL-YBFB`, `PL-YRLM` |
| `docs/ARCHITECTURE.md` | 120 | 40 | `PL-1RTM`, `PL-2H0K`, `PL-5N7T`, `PL-B5LB`, `PL-S5YM`, `PL-TPS7`, `PL-ZBBP` |

Every one of those reads `crossing`, so neither `docket next workflow` nor
`docket next product` offers it, and each would read `workflow` were the
document on the other side. The placement is not wrong on its own terms - both
documents are written for a reader of the simulator - but each also carries
apparatus facts: `docs/ARCHITECTURE.md` documents the `tools/` tree entry by
entry (`PL-93RN` is one such entry gone stale), and release scoping in
`ROADMAP.md` is queue work that touches `docs/items` in the same change.

**Two routes, and the second is the durable one.** Reopen the placement, which
moves the 130 the other way and misplaces the product items instead; or move
the apparatus facts out of the two documents - the `tools/` entries into
`docs/worker.md` or `subprojects/docket/README.md`, which are already on the
workflow side - so the documents stop being both. `PL-TPS7` (cut the prose in
`docs/ARCHITECTURE.md` and `docs/maintainer.md`) is adjacent to the second.
Not folded into `PL-8ZGY`, whose brief places only the paths no carrier has
placed; this is a placement a carrier made, with ordinary evidence against it.

**Why it matters.** The thirteen open items the table names read `crossing`,
so neither `bin/docket next workflow` nor `next product` offers them; only the
bare `next` does.

**Decision needed.** Which route, for each document. **Recommended: route 2
for `docs/ARCHITECTURE.md`, and no change for `ROADMAP.md`.**
`ARCHITECTURE.md`'s seven are all tool work (`PL-1RTM`, `PL-2H0K`, `PL-5N7T`,
`PL-B5LB`, `PL-S5YM`, `PL-TPS7`, `PL-ZBBP`) reaching it through its `tools/`
inventory, so moving that inventory to the apparatus side lets them read
`workflow`. `ROADMAP.md`'s six are mixed: `PL-B396` (agent amounts in litres of
vapour) and `PL-YRLM` (which release builds agent cost) are product decisions
route 1 would misplace, so the ratified placement stands and the other four stay
reachable through the bare `next`. Route 1 reopens a placement the owner
ratified under `PL-8ZGY`, so it would go back to him; route 2 reopens nothing.

**Done when.** The chosen route is applied and the affected open items' lanes,
read through `Item.lane`, are recorded here.

**Generator check.** `PL-8ZGY`'s fact (which lane each tracked path is in),
filed in the commit that closed `PL-8ZGY` as the question its table deferred
here; not a post-close instance.
