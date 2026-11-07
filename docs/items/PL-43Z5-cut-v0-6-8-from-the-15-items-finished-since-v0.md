---
id: PL-43Z5
title: Cut v0.6.8 from the 15 items finished since v0.6.7
status: done
resource: release-train
added: 2026-10-25
closed: 2026-10-25
pr: 1823
verify: grep -q '^## Current baseline: v0.6.8' ROADMAP.md
---

**Problem.** Cut v0.6.8 from the 15 items finished since v0.6.7

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.8 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> 15 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: v0.7.0, the schematic, is scoped and not built, and v0.7.0 and v0.8.0 are given to milestone sections. **Nothing in `src/` changed, and no run can differ**: `src/` resolves to `7be0bb4` at the v0.6.7 tag and here. `tests/reference/` moved only in its docstrings and comments, and `tools/ast_identity.py` finds no code moved in any of its 10 files. `docs/MODEL.md` moved because `PL-BZR4` (`#1808`) rewrote its prose, keeping every equation, unit, number, marker, section heading and citation. `PL-FDMJ` and `PL-WL5L` (`#1805`) rewrote the simulator tests' prose, `PL-K7N7` (`#1822`) rewrote `ROADMAP.md`'s, and three test docstrings that stated wrong figures were corrected (`PL-FJMW`, `PL-KM19`, `PL-KYVR`). One source of truth carries five defects (`PL-3PKN`, `PL-6GP9`, `PL-H716`, `PL-2T6S`, `PL-P0RG`), `PL-H57W` closes a gap in `verify`'s mutation check, `PL-J7YG` ranks the model review on fixes that did not hold, and `PL-PV5Q` re-reads `docs/interface-provenance.md`'s Blender rationale against Blender's own pages. **It finishes `one-source-of-truth` and `prose-quality`**, and closes no generator head. **One is a Gate 3 entry**, `PL-H57W`, and with `PL-QX2G` and `PL-YT3T` added to the list by `#1820` the gate stands at 25 of 48 cleared, from 24 of 46 at the v0.6.7 tag. `PL-43Z5`, the cut, ships in no release under `PL-KRS6`.
