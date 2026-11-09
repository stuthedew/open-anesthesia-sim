---
id: PL-PZGY
title: Cut v0.6.13 from the 22 items finished since v0.6.12
status: done
resource: release-train
added: 2026-11-02
closed: 2026-11-02
pr: 1938
verify: grep -q '^## Current baseline: v0.6.13' ROADMAP.md
---

**Problem.** Cut v0.6.13 from the 22 items finished since v0.6.12

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.13 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> 22 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because the schematic milestone is not finished: 10 of the 11 ids in v0.7.0's Required scope are closed, seven of them here, and `PL-1P15`, the cost in money on the agent cost View, stays open. v0.7.0 and v0.8.0 are given to milestone sections. **No equation or model parameter changed**: `core/` (`8186a8c`) resolves to the same tree at the v0.6.12 tag and here, and `data/` moved (`2f84dbb` to `7cc6b59`) only in the Maintenance Workspace's arrangement and a docstring. **Every modelled state is bit-identical, and 19 of 271 halts, each at a MAC target, come one or two 0.1 s steps earlier**: the trajectory comparison against the v0.6.12 tag found every state vector, canonical state, drawn window, hover string and readout string identical over 81 cases and three 24-hour runs. The 19 halts moved because `PL-QVBR` gives a MAC target's height a band of one part in a hundred thousand, and a run now halts at the first step whose reading enters it. Each snapshot gains two fields, the compartment amounts and the vapour-per-liquid factor. **It finishes four features**, `generator-heads`, `guard-tool-names`, `review-hold` and `schematic`, and closes two generator heads, `PL-16BG` and `PL-B6YV`, both spent. **Seven are Gate 3 entries**, five of them in v0.7.0's Required scope, and with `PL-0KPD` dropped the gate stands at 86 of 89 cleared, from 78 of 89 at the v0.6.12 tag. `PL-PZGY`, the cut, ships in no release under `PL-KRS6`.
