---
id: PL-L7RV
title: Cut v0.5.26 from the 44 items finished since v0.5.25
status: done
resource: release-train
added: 2026-10-18
closed: 2026-10-18
pr: 1530
verify: grep -q "^version = \"0.5.26\"" pyproject.toml
---

**Problem.** Cut v0.5.26 from the 44 items finished since v0.5.25

**Done 2026-10-18.** `make release VERSION=0.5.26` stamped the items finished
since v0.5.25 and wrote `docs/releases/v0.5.26.md`. It was re-run once, after
`#1529` (`PL-PGZF`) merged under the draft, which took the filing's 43 items
to 44. The cut was started by the project's coordinator under its standing
order to cut releases when the repository's rules call for one (project owner,
2026-10-17: "make sure to cut releases when needed"). The occasion is three
features finishing: `friction-batch`, `tests-detect-wrong-values` and
`validation-resolving-power`. The version is the coordinator's default, the
next patch on the 0.5 track: no capability boundary is crossed, and
`bin/docket wave` lists 0.6.0, 0.7.0 and 0.8.0 as spent.

`ROADMAP.md` takes the row, the baseline mark and the baseline section. Seven
of the items are Gate 2 entries, and the gate stands at 220 of 241 cleared,
from 213 of 240 at the v0.5.25 tag, recounted by running that tag's own
`bin/docket wave`. `src/` resolves to `ada5e66` at v0.5.25 and here, so the
trajectories were not measured: no run can differ.

`#1497` (`PL-3KMD`, `PL-6JKB`) merged inside v0.5.25's tag span without being
stamped by it, so v0.5.25's notes gain an `### also inside this tag's span`
pointer to this release. `tools/pr_body_check.py` found that `#1515` lost its
body, and `--recover` wrote it to `docs/pr-bodies/1515.md`.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.26 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> 44 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed, because nothing in `src/` changed, so a learner sees nothing different. v0.6.0 through v0.8.0 are given to milestone sections. **No equation, parameter or stored value changed, and no run can differ**: `src/` resolves to `ada5e66` at v0.5.25 and here, so the trajectories were not re-measured. `tests/reference/` gains published-data assertions for the first 25 minutes of wash-in (`PL-R0NL`) and cases that a changed parameter must fail (`PL-9YHR`), and four tests that claimed more than they held were renamed and narrowed (`PL-RXW0`). The unit tier now fails on an agent switch that keeps the old agent's compartments (`PL-QJXS`), a MAC-awake band left at the previous agent's values (`PL-JPS2`), and a stored MAC or MAC-awake fraction that drifts from its named source (`PL-FY35`, `PL-H1JH`). **It finishes three features**, `tests-detect-wrong-values`, `validation-resolving-power` and `friction-batch`, and closes no generator head. **Seven are Gate 2 entries**, and the gate stands at 220 of 241 cleared, from 213 of 240 at the v0.5.25 tag. `PL-L7RV`, the cut, ships in no release under `PL-KRS6`.
