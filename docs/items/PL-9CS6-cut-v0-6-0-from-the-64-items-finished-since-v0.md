---
id: PL-9CS6
title: Cut v0.6.0 from the 64 items finished since v0.5.42
status: done
resource: release-train
added: 2026-10-20
closed: 2026-10-20
pr: 1700
verify: grep -q '^## Current baseline: v0.6.0' ROADMAP.md
---

**Problem.** Cut v0.6.0 from the 64 items finished since v0.5.42

**Fixed in place during the cut** (2026-10-20). The real-tree gate test,
`test_this_repository_records_a_disposition_for_every_open_debt_item`, asserted
that a gate is always current. Shipping v0.6.0 with v0.7.0 not yet scoped leaves
no section ahead of the baseline recording a frozen list, so CI failed on a
correct roadmap. The test now requires the baseline's release train and accepts
a missing gate only where that train records none.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.0 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> 64 items, and the capability boundary § "Versioning decision" gives a minor number to: all 40 ids in v0.6.0's Required scope are closed. **No equation, parameter or stored scientific value changed, and no run differs**: `core/` moved (`92e04de` to `d482c41`) because its refusals now name the object that refused and reject a capacity that underflows or overflows (`#1676`), and the trajectory comparison against the v0.5.42 tag found every state, halt, readout and hover string identical over 81 cases and three 24-hour runs. `data/` resolves to `bd5d496` at both ends. A learner can now save, restore and reset Workspaces from the Layout menu (`PL-DWHG`), open the Area and Layout menus by right-click and swap two Areas by Ctrl-drag (`PL-R5G4`), and no longer meets an Area too thin to see (`PL-391Y`). The region holding time, run state, agent and concentrations sits above the part of the page that scrolls and the disclaimer sits below it, so neither leaves the window at any height (`PL-NNML`). **It finishes five features**, among them `layout-sliver-areas` and `v0.6.0-done-check`, the check of the Definition of done bullet by bullet that found `PL-NNML`. **Gate 2 is clear**: 241 of its 247 entries are cleared and 6 are deferred, from 239 of 246 at the v0.5.42 tag. `PL-9CS6`, the cut, ships in no release under `PL-KRS6`.
