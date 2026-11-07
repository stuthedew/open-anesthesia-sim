---
id: PL-1BL8
title: Cut v0.5.30 from the 3 items finished since v0.5.29
status: done
resource: release-train
added: 2026-10-18
closed: 2026-10-18
pr: 1610
verify: grep -q "^version = \"0.5.30\"" pyproject.toml
---

**Problem.** Cut v0.5.30 from the 3 items finished since v0.5.29

**Done 2026-10-18.** `make release VERSION=0.5.30` stamped the 3 items
finished since v0.5.29 and wrote `docs/releases/v0.5.30.md`. The coordinator
started the cut under the project owner's standing order to cut releases when
the repository's rules call for one (2026-10-17: "make sure to cut releases
when needed"). The occasion is the `claim-integrity` feature finishing with
`PL-JLK6`. The version is the coordinator's default, the next patch on the 0.5
track: no capability boundary is crossed, and `bin/docket wave` lists 0.6.0,
0.7.0 and 0.8.0 as spent.

`ROADMAP.md` takes the row, the baseline mark and the baseline section. One
item, `PL-QLZ5`, is a Gate 2 entry, and the gate stands at 233 of 246 cleared,
from 232 of 246 at the v0.5.29 tag. `core/`, `data/` and `layout/` resolve to
the same trees at the v0.5.29 tag and here, so the trajectories were not
measured again. `#1607` merged after v0.5.29's cut was written and before it
landed, so it ships inside the v0.5.29 tag, and v0.5.29's notes now point to
this release for `PL-JLK6` and `PL-JTWV`.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.30 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Three items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because a layout the reader arranges is not finished: 27 of the 39 ids in v0.6.0's Required scope are closed. v0.6.0 through v0.8.0 are given to milestone sections. **No equation, parameter or stored value changed, and no run can differ**: `core/` resolves to `92e04de` at v0.5.29 and here, and `data/` and `layout/` resolve to the same trees, so the trajectories were not re-measured. `app/` changed (`6d1a9c6` to `48d6a4a`) because in compare mode each run's transport controls and delivered concentration share one line, and the substance, 1 MAC and model the two runs share are stated once above the paired readouts (`PL-QLZ5`). On the 1366 by 700 reference that takes the region from 366 px to 303 px and leaves the chart about 264 px, still under the 360 px one run keeps, which the project owner accepted (`PL-JG82`). **It finishes `claim-integrity`**, and closes no generator head. **One is a Gate 2 entry**, and the gate stands at 233 of 246 cleared, from 232 of 246 at the v0.5.29 tag. `PL-JLK6` and `PL-JTWV` shipped inside the v0.5.29 tag and are described here. `PL-1BL8`, the cut, ships in no release under `PL-KRS6`.
