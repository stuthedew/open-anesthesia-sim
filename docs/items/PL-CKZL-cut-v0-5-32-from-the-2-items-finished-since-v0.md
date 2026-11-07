---
id: PL-CKZL
title: Cut v0.5.32 from the 2 items finished since v0.5.31
status: done
resource: release-train
added: 2026-10-19
closed: 2026-10-19
pr: 1623
verify: grep -q "^version = \"0.5.32\"" pyproject.toml
---

**Problem.** Cut v0.5.32 from the 2 items finished since v0.5.31

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.32 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> Two items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because a layout the reader arranges is not finished: 31 of the 39 ids in v0.6.0's Required scope are closed. v0.6.0 through v0.8.0 are given to milestone sections. **No equation, parameter or stored value changed, and no run can differ**: `core/` resolves to `92e04de` at v0.5.31 and here, and `data/` and `layout/` resolve to the same trees, so the trajectories were not re-measured. `app/` changed (`89ae293` to `64a6e74`) because each Area builds its View from that View's registry entry, and the concentration chart, the wash-in plot, the parameter controls and the agent accounting each meet the `View` protocol in `app/view_contract.py` (`PL-TH35`). **It finishes `review-hold`**, and closes no generator head. **One is a Gate 2 entry**, and the gate stands at 237 of 246 cleared, from 236 of 246 at the v0.5.31 tag. `PL-CKZL`, the cut, ships in no release under `PL-KRS6`.
