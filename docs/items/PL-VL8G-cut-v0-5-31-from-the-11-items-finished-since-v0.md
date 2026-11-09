---
id: PL-VL8G
title: Cut v0.5.31 from the 11 items finished since v0.5.30
status: done
resource: release-train
added: 2026-10-19
closed: 2026-10-19
pr: 1621
verify: grep -q "^version = \"0.5.31\"" pyproject.toml
---

**Problem.** Cut v0.5.31 from the 10 items finished since v0.5.30

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.31 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> 11 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because a layout the reader arranges is not finished: 30 of the 39 ids in v0.6.0's Required scope are closed. v0.6.0 through v0.8.0 are given to milestone sections. **No equation, parameter or stored value changed, and no run can differ**: `core/` resolves to `92e04de` at v0.5.30 and here, and `data/` and `layout/` resolve to the same trees, so the trajectories were not re-measured. `app/` changed (`48d6a4a` to `89ae293`) because each Area's header carries a View chooser and a build without the accounting View fails (`PL-50PZ`), and because a widened chart is redrawn at its own width, the time base is held outside its selector, and each of a run's four Area surfaces can be built more than once (`PL-9LNF`), and the dashboard marks each string it holds with whether a reader can see it now, which changes nothing on screen (`PL-904Y`). **It finishes `test-effectiveness-measurement`**, and closes no generator head. **Three are Gate 2 entries**, and the gate stands at 236 of 246 cleared, from 233 of 246 at the v0.5.30 tag. `PL-QT2J` shipped inside the v0.5.30 tag and is described here. `PL-VL8G`, the cut, ships in no release under `PL-KRS6`.
