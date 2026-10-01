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
