---
id: PL-HFQ9
title: Cut v0.5.27 from the 5 items finished since v0.5.26
status: done
resource: release-train
added: 2026-10-18
closed: 2026-10-18
pr: 1535
verify: grep -q "^version = \"0.5.27\"" pyproject.toml
---

**Problem.** Cut v0.5.27 from the 5 items finished since v0.5.26

**Done 2026-10-18.** `make release VERSION=0.5.27` stamped the five items
finished since v0.5.26 and wrote `docs/releases/v0.5.27.md`. The cut was
started by the project's coordinator under its standing order to cut releases
when the repository's rules call for one (project owner, 2026-10-17: "make sure
to cut releases when needed"). The occasion is `validation-resolving-power`
finishing a second time, since `PL-CM1B` joined it after v0.5.26. The version
is the coordinator's default, the next patch on the 0.5 track: no capability
boundary is crossed, and `bin/docket wave` lists 0.6.0, 0.7.0 and 0.8.0 as
spent.

`ROADMAP.md` takes the row, the baseline mark and the baseline section. Three
of the items are Gate 2 entries, and the gate stands at 223 of 243 cleared,
from 220 of 241 at the v0.5.26 tag, recounted by running that tag's own
`bin/docket wave`. `src/` moved only in `data/`, and a field-by-field
comparison of the five changed files against the tag found only source
entries, notes and provenance-gap text, so the trajectories were not measured.
No pull request merged inside v0.5.26's tag span unstamped, and
`tools/pr_body_check.py` found no squash commit that lost its body.
