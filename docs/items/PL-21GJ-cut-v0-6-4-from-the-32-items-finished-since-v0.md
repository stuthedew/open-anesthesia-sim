---
id: PL-21GJ
title: Cut v0.6.4 from the 32 items finished since v0.6.3
status: done
resource: release-train
added: 2026-10-25
closed: 2026-10-25
pr: 1786
verify: grep -q '^## Current baseline: v0.6.4' ROADMAP.md
---

**Problem.** Cut v0.6.4 from the 32 items finished since v0.6.3

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.4 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> 32 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: v0.7.0, the schematic, is scoped and not built, and v0.7.0 and v0.8.0 are given to milestone sections. **No equation, parameter or stored value changed, and no run differs**: `core/` moved (`d482c41` to `c5e1538`) because its input checks now each have one home (`#1772`), its refusals name the refused value (`#1775`) and each MAC is a `MacPercent` (`#1784`), and the trajectory comparison against the v0.6.3 tag found every state, readout and hover string bit-identical over 81 cases and three 24-hour runs, the snapshot's MAC differing only in its type. `data/` resolves to `bd5d496` at both ends. An agent change now clears the branch panel's refusal notice, and a halted run shows the current playback rate (`PL-BM6X`, `PL-P58M`). Three items merged inside the v0.6.3 tag's span and are described here (`PL-LF0P`, `PL-YRLM`, `PL-SC0N`). **It finishes six features**, among them `parse-dont-validate` and `documentation-standard`, and closes four generator heads, all spent (`PL-CMJ5`, `PL-GTH6`, `PL-R0BJ`, `PL-VDWT`). **Sixteen are Gate 3 entries**, and the gate stands at 18 of 46 cleared, from 3 of 46 at the v0.6.3 tag. `PL-21GJ`, the cut, ships in no release under `PL-KRS6`.
