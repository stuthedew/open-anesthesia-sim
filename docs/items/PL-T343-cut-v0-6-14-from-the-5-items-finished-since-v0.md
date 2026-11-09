---
id: PL-T343
title: Cut v0.6.14 from the 5 items finished since v0.6.13
status: done
resource: release-train
added: 2026-11-02
closed: 2026-11-02
pr: 1941
verify: grep -q '^## Current baseline: v0.6.14' ROADMAP.md
---

**Problem.** Cut v0.6.14 from the 5 items finished since v0.6.13

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.14 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> Five items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because the schematic milestone is not finished: 10 of the 11 ids in v0.7.0's Required scope are closed, and `PL-1P15`, the cost in money on the agent cost View, stays open. v0.7.0 and v0.8.0 are given to milestone sections. **No code, stored value or displayed value changed, and no run can differ**: `core/` (`8186a8c`) resolves to the same tree at the v0.6.13 tag and here. `data/` moved (`7cc6b59` to `c3fbdbc`) only in the three agent files' `sources` notes and `provenance_gap` text, and `tools/ast_identity.py` finds no code moved in `app/control_timeline.py` or `tests/reference/test_coupled_dynamics.py`, so the trajectories were not re-measured. **It finishes two features**, `drift-2026-11-01` and `stale-source-claims`, and closes no generator head. **None is a Gate 3 entry**, and the gate stands at 86 of 89 cleared, as at the v0.6.13 tag. `PL-T343`, the cut, ships in no release under `PL-KRS6`.
