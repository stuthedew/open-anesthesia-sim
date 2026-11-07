---
id: PL-8B6Z
title: Cut v0.6.15 from the 98 items finished since v0.6.14
status: done
resource: release-train
added: 2026-11-04
closed: 2026-11-04
pr: 2036
verify: grep -q '^## Current baseline: v0.6.15' ROADMAP.md
---

**Problem.** Cut v0.6.15 from the 98 items finished since v0.6.14

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.15 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> 98 items, and a patch on both halves of § "Versioning decision"'s test, cut before v0.7.0 at the project owner's word (project owner, 2026-11-04). No capability boundary is crossed: the 11 ids that v0.7.0's Required scope named before this cut are now closed, `PL-1P15` among them, and the project owner has since added the copy editor's fix and the five `docs/MODEL.md` rewrites it blocks, which stay open (`PL-YXPN`, `#2037`). v0.7.0 is cut only after the project owner has test-driven `main`. v0.7.0 and v0.8.0 are given to milestone sections. **No equation, model parameter or stored value changed, and no modelled state can differ**: `core/` (`8186a8c`) and `data/` (`c3fbdbc`) resolve to the same trees at the v0.6.14 tag and here, so the trajectories were not re-measured. `src/` moved only in `app/`, for the cost in money (`PL-1P15`, `#1939`). **It finishes eleven features**, among them `owner-ask-by-state`, `guards-keyed-on-the-action` and `dead-test-limits`, and closes four generator heads, all spent (`PL-1ZZ0`, `PL-9KSJ`, `PL-H76S`, `PL-ZCF9`). **One is a Gate 3 entry**, `PL-1P15`, and with `PL-SP6H` added to the list the gate stands at 87 of 90 cleared, from 86 of 89 at the v0.6.14 tag. `PL-8B6Z`, the cut, ships in no release under `PL-KRS6`.
