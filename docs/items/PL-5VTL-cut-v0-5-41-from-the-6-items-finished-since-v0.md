---
id: PL-5VTL
title: Cut v0.5.41 from the 6 items finished since v0.5.40
status: done
resource: release-train
added: 2026-10-19
closed: 2026-10-19
pr: 1658
verify: grep -q "^version = \"0.5.41\"" pyproject.toml
---

**Problem.** Cut v0.5.41 from the 6 items finished since v0.5.40

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.41 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> Six items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because a layout the reader arranges is not finished: 36 of the 39 ids in v0.6.0's Required scope are closed. v0.6.0 through v0.8.0 are given to milestone sections. **No equation, parameter or stored value changed, and no run can differ**: `core/` resolves to `92e04de` at the v0.5.40 tag and here, and `tests/reference/` to `b0c7cb3`, so the trajectories were not re-measured. `data/` moved only in `data/workspaces/`, whose three Workspaces gain a schema version and an empty pin. `app/` and `layout/` changed because each run is named by an identity that is never reused and a Workspace can pin one (`PL-7Z84`), the dashboard opens on the shipped Workspaces under a tab strip where a reader sets a pin (`PL-2KXB`), each Area border can be moved from the keyboard and a Layout menu switches Workspace (`PL-M352`), and `AreaLayout` refuses a layout of two windows before it builds its widget, which had crashed a test worker on `main` (`PL-H9VT`). `docs/MODEL.md` states the run identity and the pin. **It finishes `owner-attention`**, and closes no generator head. **One is a Gate 2 entry**, `PL-7Z84`, and the gate stands at 239 of 246 cleared, from 238 of 246 at the v0.5.40 tag. `PL-5VTL`, the cut, ships in no release under `PL-KRS6`.
