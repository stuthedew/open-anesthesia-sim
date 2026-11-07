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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.28 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> 70 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: the flows are formed from the same equation as before, and the new refusal sits on a route no shipped profile takes. v0.6.0 through v0.8.0 are given to milestone sections. **No equation, parameter or stored value changed, and every state a run plays is bit-identical**: `core/` changed (`60697e5` to `1ebb078`) because a compartment's flow is now `f_i × Q` formed where it is used, a perfusion fraction can be written only when its group is built, and the patient refuses a tissue set whose fractions do not sum to 1 (`PL-HQF5`, `PL-Z0HN`); `app/` changed (`3b03e6f` to `a96792e`) because the dashboard refuses a machine profile whose opening fresh gas flow is not one of its slider's steps (`PL-1KQ9`). Over 81 runs across the three agents, each with two branches, all 6,561,000 steps, 11,253 sampled states, 11,178 canonical states, 2,187 drawn windows and 19,448,865 formatted strings are identical at both ends, as are three 24-hour runs. `data/`, `layout/`, `tests/reference/` and `README.md` resolve to the same trees. **It finishes thirteen features**, among them `cardiac-output-write-consistency`, and records two live generator heads, `PL-RJLQ` and `PL-ZQ3R`, while closing `PL-MLR4` as spent. **Two are Gate 2 entries**, and the gate stands at 225 of 243 cleared, from 223 of 243 at the v0.5.27 tag. `PL-SVZD`, the cut, ships in no release under `PL-KRS6`.
