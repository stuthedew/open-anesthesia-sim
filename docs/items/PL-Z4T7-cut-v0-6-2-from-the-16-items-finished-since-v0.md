---
id: PL-Z4T7
title: Cut v0.6.2 from the 16 items finished since v0.6.1
status: done
resource: release-train
added: 2026-10-24
closed: 2026-10-24
pr: 1749
verify: grep -q '^## Current baseline: v0.6.2' ROADMAP.md
---

**Problem.** Cut v0.6.2 from the 16 items finished since v0.6.1

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.2 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> 16 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: v0.7.0, the schematic, was not yet scoped when it was cut, and v0.7.0 and v0.8.0 are given to milestone sections. **No equation, parameter or stored value changed, and no run can differ**: `src/anesthesia_sim/core/`, `src/anesthesia_sim/data/`, `tests/reference/`, `docs/MODEL.md` and `README.md` resolve to the same trees at the v0.6.1 tag and here. `src/` moved only in `app/`, where `PL-4X5B` named 29 bare layout literals without changing a value, and rendered the default run pixel-identical before and after. The owner-ask hook (`PL-YGR6`, `PL-YV90`, `PL-646J`, `PL-JLB4`), triage's defect class for a second copy (`PL-ZZ03`), the two drained baselines (`PL-LGDV`, `PL-4X5B`), `verify`'s mutation run on changed lines (`PL-CZXN`), and the effort trial's arm drawn in the session-start hook (`PL-8MZ9`) carry it. **It finishes `review-hold`**, and closes no generator head. **None is a gate entry**: Gate 3 froze later, when v0.7.0 was scoped. `PL-Z4T7`, the cut, ships in no release under `PL-KRS6`.
