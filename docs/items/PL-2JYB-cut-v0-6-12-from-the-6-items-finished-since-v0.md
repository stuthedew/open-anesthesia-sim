---
id: PL-2JYB
title: Cut v0.6.12 from the 6 items finished since v0.6.11
status: done
resource: release-train
added: 2026-11-01
closed: 2026-11-01
pr: 1914
verify: grep -q '^## Current baseline: v0.6.12' ROADMAP.md
---

**Problem.** Cut v0.6.12 from the 6 items finished since v0.6.11

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.12 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Six items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: v0.7.0, the schematic, is scoped and not built, and v0.7.0 and v0.8.0 are given to milestone sections. **No equation, parameter or stored value changed, and no run can differ**: `core/` (`8186a8c`) and `data/` (`2f84dbb`) resolve to the same trees at the v0.6.11 tag and here, so the trajectories were not re-measured. `src/` moved only in `app/area_layout.py` and `layout/sizing.py`, for the Area borders and floors. **It finishes two features**, `invariant-test-gaps` and `model-review`, and closes no generator head. **None is a Gate 3 entry**, though three were deferred from it, and the gate stands at 78 of 89 cleared, as at the v0.6.11 tag. `PL-2JYB`, the cut, ships in no release under `PL-KRS6`.
