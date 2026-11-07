---
id: PL-8BDX
title: Cut v0.6.10 from the 12 items finished since v0.6.9
status: done
resource: release-train
added: 2026-10-31
closed: 2026-10-31
pr: 1903
verify: grep -q '^## Current baseline: v0.6.10' ROADMAP.md
---

**Problem.** Cut v0.6.10 from the 12 items finished since v0.6.9

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.10 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> 12 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: v0.7.0, the schematic, is scoped and not built, and v0.7.0 and v0.8.0 are given to milestone sections. **No stored value changed, and every modelled state and displayed string is bit-identical**: `core/` moved (`dbba1c0` to `26931f6`) only in the accounting error, which now carries the failing check and says the step was rolled back, and `data/` is unchanged (`2f84dbb`). The trajectory comparison against the v0.6.9 tag found every state vector, canonical state, drawn window, hover string, readout string and halt identical over 81 cases and three 24-hour runs. A snapshot gains one field, the rejected step's check, which no case in the comparison fills. **It finishes two features**, `mac-awake-reference-text` and `one-source-of-truth`, and closes one generator head, spent (`PL-J5GC`). **Nine are Gate 3 entries**, none in v0.7.0's Required scope, and the gate stands at 73 of 88 cleared, from 64 of 87 at the v0.6.9 tag. `PL-8BDX`, the cut, ships in no release under `PL-KRS6`.
