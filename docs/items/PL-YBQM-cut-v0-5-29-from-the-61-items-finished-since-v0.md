---
id: PL-YBQM
title: Cut v0.5.29 from the 61 items finished since v0.5.28
status: done
resource: release-train
added: 2026-10-18
closed: 2026-10-18
pr: 1605
verify: grep -q "^version = \"0.5.29\"" pyproject.toml
---

**Problem.** Cut v0.5.29 from the 61 items finished since v0.5.28

**Done 2026-10-18.** `make release VERSION=0.5.29` stamped the 61 items
finished since v0.5.28 and wrote `docs/releases/v0.5.29.md`. The coordinator
started the cut under its standing order to cut releases when the repository's
rules call for one (project owner, 2026-10-17: "make sure to cut releases when
needed"). The occasion is sixteen features finishing, among them
`reset-aftermath`. The owner had to point out that the release was overdue, so
`PL-8T56` records that nothing raises a release at the moment a feature
finishes. The version is the coordinator's default, the next patch on the 0.5
track: no capability boundary is crossed, and `bin/docket wave` lists 0.6.0,
0.7.0 and 0.8.0 as spent.

The first cut took 59 items. `#1604` merged while the release was in draft, so
the cut was re-run at 61 to take `PL-F2YS` and `PL-JG82`. `ROADMAP.md` takes
the row, the baseline mark and the baseline section. Seven of the items are
Gate 2 entries, and the gate stands at 232 of 246 cleared, from 225 of 243 at
the v0.5.28 tag. `core/` moved (`PL-XRN8`), so the trajectories were measured
against the v0.5.28 tag with the kept script: all 81 runs, 6,561,000 steps and
three 24-hour runs are bit-identical. Two pull requests inside v0.5.28's tag
span, `#1553` and `#1572`, now have pointer lines in its notes.
