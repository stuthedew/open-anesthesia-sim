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
