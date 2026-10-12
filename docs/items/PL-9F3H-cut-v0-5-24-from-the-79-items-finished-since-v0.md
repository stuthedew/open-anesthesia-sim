---
id: PL-9F3H
title: Cut v0.5.24 from the 79 items finished since v0.5.23
status: done
resource: release-train
added: 2026-10-12
closed: 2026-10-12
pr: 1468
verify: grep -q "^version = \"0.5.24\"" pyproject.toml
---

**Problem.** Cut v0.5.24 from the 79 items finished since v0.5.23

**Done 2026-10-12.** `make release VERSION=0.5.24` stamped the items finished
since v0.5.23 and wrote `docs/releases/v0.5.24.md`. It was re-run once, as
`#1463` (`PL-0HLS`, `PL-9VPH`, `PL-SV0D`, `PL-TS7L`) merged under the draft,
taking the filing's 75 items to 79. The version is the patch the project owner
chose ("Cut now" on the coordinator's card, 2026-10-12 20:44Z): no capability
boundary is crossed, and `bin/docket wave` lists 0.6.0, 0.7.0 and 0.8.0 as
spent.

`ROADMAP.md` takes the row, the baseline mark and the baseline section. Eleven
are Gate 2 entries; the gate stands at 204 of 229 cleared, from 197 of 222 at
the v0.5.23 tag. `core/` moved (`0e9255d` to `a0e4719`), so the trajectories
were measured against the tag: 81 runs and a branch from each, and three
24-hour runs, compared as exact bits. Every sampled state, canonical state,
drawn window and formatted readout string is identical; the snapshot differs
only by its new `accepted_fresh_gas_flow_range_l_min` field (`PL-7CRY`).

`#1420` (`PL-WXKD`) merged inside v0.5.23's tag span without being stamped by
it, so v0.5.23's notes gain an `### also inside this tag's span` pointer to
this release. `tools/pr_body_check.py` named `#1450`'s squash commit as
bodiless; GitHub holds no body for it either, which `docs/pr-bodies/1450.md`
records.
