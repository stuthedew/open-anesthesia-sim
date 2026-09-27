---
id: PL-KRGY
title: ROADMAP.md and docs/ARCHITECTURE.md's product placement in workflow_paths sets aside 90 and 40 items that pair them only with apparatus paths - 14 open - because both documents also carry apparatus facts, so the deliberate absence written when it cost four items now costs the crossing set most of its members
status: untriaged
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
