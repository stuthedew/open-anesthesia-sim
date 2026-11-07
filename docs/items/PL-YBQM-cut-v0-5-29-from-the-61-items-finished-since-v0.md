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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.29 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> 61 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because a layout the reader arranges is not finished: 26 of the 39 ids in v0.6.0's Required scope are closed. v0.6.0 through v0.8.0 are given to milestone sections. **No equation, parameter or stored value changed, and every state a run plays is bit-identical**: `core/` changed (`1ebb078` to `92e04de`) because `AgentUptakeSystem.settings_key()` lets the controller halt a run before a step at settings its definition never recorded (`PL-XRN8`). The band (`PL-NWTM`, `PL-W54S`), the live borders (`PL-W9P6`, `PL-L8RN`), the View registry (`PL-R1WQ`) and the shared readout row (`PL-F2YS`) change `app/`; three default Workspaces ship as data in `data/` and `layout/`, which no part of the interface reads yet (`PL-KXTL`). A learner also sees Branch scroll the chart into view (`PL-562Z`), the trunk's Reset ask before it discards a branch (`PL-W5WX`), no branch offered on a failed frame (`PL-T2Q2`), and a late mark read the same way on every run (`PL-1ZQ4`). **It finishes sixteen features**, among them `reset-aftermath`, and closes two generator heads spent, `PL-ZQ3R` and `PL-RJLQ`. **Seven are Gate 2 entries**, and the gate stands at 232 of 246 cleared, from 225 of 243 at the v0.5.28 tag. `PL-YBQM`, the cut, ships in no release under `PL-KRS6`.
