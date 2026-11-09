---
id: PL-TC7Y
title: Cut v0.6.3 from the 20 items finished since v0.6.2
status: done
resource: release-train
added: 2026-10-25
closed: 2026-10-25
pr: 1770
verify: grep -q '^## Current baseline: v0.6.3' ROADMAP.md
---

**Problem.** Cut v0.6.3 from the 20 items finished since v0.6.2

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.3 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> 20 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: v0.7.0, the schematic, is scoped and not built, and v0.7.0 and v0.8.0 are given to milestone sections. **No equation, parameter or stored value changed, and no run can differ**: `src/anesthesia_sim/core/`, `src/anesthesia_sim/data/`, `tests/reference/` and `docs/MODEL.md` resolve to the same trees at the v0.6.2 tag and here. `src/` moved only in `app/`, where two dialogs now share one layout function (`#1765`, under the still-open `PL-VWXL`), and both rendered pixel-identical at the v0.6.2 tag and here. One source of truth carries twelve items (`PL-N4FP`, `PL-MM3Q`, `PL-H5T9`, `PL-PNGQ`, `PL-SH0W` among them), the review panel three (`PL-TBQS`, `PL-TDV9`, `PL-HDRN`), and `PL-7FPD` makes `verify` refuse a branch that weakens a display test. **It finishes `blocked-means-blocked` and `review-panel`**, and closes one generator head, `PL-N4FP`, spent. **Two are Gate 3 entries**, `PL-LL9F` and `PL-YF16`: Gate 3 froze when v0.7.0 was scoped in `#1761`, after this cut was written, and with `PL-SC0N` (`#1769`, inside this tag's span) it stands at 3 of 46 cleared. `PL-TC7Y`, the cut, ships in no release under `PL-KRS6`.
