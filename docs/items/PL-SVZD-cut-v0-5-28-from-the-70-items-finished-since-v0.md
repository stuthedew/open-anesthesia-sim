---
id: PL-SVZD
title: Cut v0.5.28 from the 70 items finished since v0.5.27
status: done
resource: release-train
added: 2026-10-18
closed: 2026-10-18
pr: 1573
verify: grep -q "^version = \"0.5.28\"" pyproject.toml
---

**Problem.** Cut v0.5.28 from the 70 items finished since v0.5.27

**Done 2026-10-18.** `make release VERSION=0.5.28` stamped the 70 items
finished since v0.5.27 and wrote `docs/releases/v0.5.28.md`. The cut was
started by the project's coordinator under its standing order to cut releases
when the repository's rules call for one (project owner, 2026-10-17: "make sure
to cut releases when needed"), after the owner asked whether a new version was
due. The occasion is thirteen features finishing, among them
`cardiac-output-write-consistency`. The version is the coordinator's default,
the next patch on the 0.5 track: no capability boundary is crossed, and
`bin/docket wave` lists 0.6.0, 0.7.0 and 0.8.0 as spent.

`ROADMAP.md` takes the row, the baseline mark and the baseline section. Two of
the items are Gate 2 entries, and the gate stands at 225 of 243 cleared, from
223 of 243 at the v0.5.27 tag, recounted by running that tag's own
`bin/docket wave`. `core/` moved in `#1537`, so the trajectories were measured
on the v0.5.27 tag and on this cut with the script v0.5.25's cut used: 81 runs
with two branches each and three 24-hour runs, 0 differences in any step,
sampled state, drawn window or formatted string. `tools/doc_check.py` found no
pull request inside v0.5.27's tag span left undescribed, and
`tools/pr_body_check.py` found no squash commit that lost its body.
