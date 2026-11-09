---
id: PL-9354
title: Cut v0.5.42 from the 1 item finished since v0.5.41
status: done
resource: release-train
added: 2026-10-19
closed: 2026-10-19
pr: 1664
verify: grep -q "^version = \"0.5.42\"" pyproject.toml
---

**Problem.** Cut v0.5.42 from the 1 item finished since v0.5.41

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.42 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> One item, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because a layout the reader arranges is not finished: 37 of the 39 ids in v0.6.0's Required scope are closed. v0.6.0 through v0.8.0 are given to milestone sections. **No equation, parameter or stored scientific value changed, and no run can differ**: `core/` resolves to `92e04de` at the v0.5.41 tag and here, and `tests/reference/` to `b0c7cb3`, so the trajectories were not re-measured. `data/` moved only in `data/workspaces/induction.json`, which saves its concentration chart at the 15-minute window. `app/` changed because each chart View now saves its own window, the F_A/F_I plot gains the same control, and the off-scale notice, the wash-in state line and the count of unmarked control changes now describe each chart's own window (`PL-L59K`). `docs/MODEL.md` and `README.md` say the window is chosen for each chart. **It finishes no feature**, and closes no generator head. **It is not a Gate 2 entry**, and the gate stands at 239 of 246 cleared, as at the v0.5.41 tag. `PL-9354`, the cut, ships in no release under `PL-KRS6`.
