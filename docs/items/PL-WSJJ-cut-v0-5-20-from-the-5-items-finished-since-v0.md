---
id: PL-WSJJ
title: Cut v0.5.20 from the 5 items finished since v0.5.19
status: done
resource: release-train
added: 2026-10-01
closed: 2026-10-01
pr: 1252
verify: grep -q "^version = \"0.5.20\"" pyproject.toml
---

**Problem.** Cut v0.5.20 from the 5 items finished since v0.5.19

**Done 2026-10-01.** `make release VERSION=0.5.20` stamped the five items
finished since v0.5.19 and wrote `docs/releases/v0.5.20.md`; `ROADMAP.md`
takes the row, the baseline mark and the baseline section. `src/`,
`tests/reference/`, `docs/MODEL.md` and `README.md` resolve to the same trees
on the v0.5.19 tag and on this cut, so no trajectory was re-run. None of the
five merged inside v0.5.19's tag. This is the first cut `tag-release.yml`
(`PL-2FY6`) tags on merge.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.20 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Five items, and a patch on both halves of § "Versioning decision"'s test: nothing a learner can reach looks different, and v0.6.0 through v0.8.0 are given to milestone sections. **Nothing in the simulator moved**: `src/` resolves to `07f4da7` at v0.5.19 and here, and `tests/reference/` (`3613c87`), `docs/MODEL.md` (`1ec5a21`) and `README.md` (`3a8f16e`) with it; `.github/` moves only by `tag-release.yml`, which tags each cut on its merge (`PL-2FY6`). `PL-WT9L` closed the v0.5.19 tag step, the last of its kind; `PL-MTHC` sends `claim` and `stranded` to the open pull request carrying an item; `PL-ZZHZ` aligns the skill's restart recipe with the branch sweep; and `PL-Q7V1` weighs both human fat-flow sources in the varying-perfusion note. **One is a Gate 2 entry**, `PL-Q7V1`, and the gate stands at 123 of 194 cleared.
