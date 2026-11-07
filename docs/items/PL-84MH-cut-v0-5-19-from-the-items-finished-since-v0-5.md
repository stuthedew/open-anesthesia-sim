---
id: PL-84MH
title: Cut v0.5.19 from the items finished since v0.5.18, including PL-S17R's #1242
status: done
resource: release-train
added: 2026-09-30
closed: 2026-09-30
pr: 1246
verify: grep -q "^version = \"0.5.19\"" pyproject.toml
---

**Problem.** Cut v0.5.19 from the items finished since v0.5.18, including PL-S17R's #1242

**Done 2026-09-30.** Waited for `PL-S17R`'s `#1242` to merge so it ships
here, as the owner asked, then `make release VERSION=0.5.19` stamped the
thirteen items and wrote `docs/releases/v0.5.19.md`; `ROADMAP.md` takes the
row, the baseline mark and the baseline section. `src/`, `tests/reference/`,
`docs/MODEL.md` and `README.md` resolve to the same trees on the v0.5.18 tag
and on this cut, so no trajectory was re-run. `PL-245B` (`#1235`) and
`PL-J3TV` (`#1238`) merged inside v0.5.18's tag, and v0.5.18's notes now
point here for both. `tools/pr_body_check.py` found no lost body. Before
filing, `bin/docket flight` showed only `PL-S17R` in flight and no rival
holder of the release train. `make check` passed: 5,713 tests, 100% core
coverage. The tag step is `PL-WT9L`.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.19 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Thirteen items, all apparatus and documentation, and a patch on both halves of § "Versioning decision"'s test: nothing a learner can reach looks different, and v0.6.0 through v0.8.0 are given to milestone sections. **Nothing in the simulator moved**: `src/` resolves to `07f4da7` at v0.5.18 and here, and `tests/reference/` (`3613c87`), `docs/MODEL.md` (`1ec5a21`) and `README.md` (`3a8f16e`) with it; `.github/` moves only by `quality.yml` failing a contrast shortfall entry added in the change that introduces its colour (`PL-VJFQ`). `PL-S17R` refuses `merge_pull_request` with a hook naming the owner's Squash and merge; `PL-8JY7` and `PL-RWBV` have `docket check` advise on a `touches` path the tree no longer holds; `PL-SYG4` names the next free patch number where a reserved version held the release offer back; and `PL-GR0L` completes `fewer-red-runs`. **Seven are Gate 2 entries**, and the gate stands at 122 of 194 cleared; `PL-245B` and `PL-J3TV` shipped inside the v0.5.18 tag.
