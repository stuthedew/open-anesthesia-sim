---
id: PL-KDDS
title: Cut v0.6.11 from the 14 items finished since v0.6.10
status: done
resource: release-train
added: 2026-11-01
closed: 2026-11-01
pr: 1910
verify: grep -q '^## Current baseline: v0.6.11' ROADMAP.md
---

**Problem.** Cut v0.6.11 from the 14 items finished since v0.6.10

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.11 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> 14 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: v0.7.0, the schematic, is scoped and not built, and v0.7.0 and v0.8.0 are given to milestone sections. **No stored value changed, and every modelled state and displayed string is bit-identical**: `core/` moved (`26931f6` to `8186a8c`) only for `PL-9B1M`'s input ceiling and the new check on every drawn column, which no shipped vaporizer's maximum reaches, and `data/` is unchanged (`2f84dbb`). The trajectory comparison against the v0.6.10 tag found every state vector, canonical state, drawn window, hover string, readout string, halt and snapshot field identical over 81 cases and three 24-hour runs. **It finishes two features**, `floating-point-domain` and `numerical-domain`, and closes no generator head. **Five are Gate 3 entries**, none in v0.7.0's Required scope, and the gate stands at 78 of 89 cleared, from 73 of 88 at the v0.6.10 tag. `PL-KDDS`, the cut, ships in no release under `PL-KRS6`.
