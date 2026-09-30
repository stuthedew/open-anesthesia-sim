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
