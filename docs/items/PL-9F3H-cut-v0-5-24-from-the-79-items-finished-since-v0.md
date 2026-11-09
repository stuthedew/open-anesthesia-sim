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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.24 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> 79 items, and a patch on both halves of § "Versioning decision"'s test: no capability boundary is crossed, since each new fork is v0.5.0's bookmark fork taken at an instant the case has reached, and v0.6.0 through v0.8.0 are given to milestone sections. **No equation, parameter or stored value moved, and every sampled state is bit-identical**: `core/` changes (`0e9255d` to `a0e4719`) because the alveolar and tissue agent amounts are held to the compartment's capacity where they are written (`PL-544D`), the two concentration crossings refuse a bare `float` (`PL-1DP1`) and the circuit states once the fresh gas flow range it accepts (`PL-7CRY`). Over 81 runs across the three agents and a branch from each, all 9,720 sampled states, 7,371 canonical states, 23,328 drawn windows and 155,520 readout strings are identical at both ends, as are three 24-hour runs, the snapshot differing only by the new accepted-range field. What a learner can see change is the two new places to branch (`PL-Y2SL`, `PL-2N43`, `PL-W4XQ`) and a control on a halted run restating the halt (`PL-V2HC`); `data/` (`7540b37`) and `tests/reference/` (`b4b0046`) resolve to the same trees, and `README.md` gains the quality badge. **It finishes five features, one of them the simulator's**, `qt-port`, and closes five generator heads spent, `PL-ZGYX`, `PL-4S6C`, `PL-8QMD`, `PL-0HLS` and `PL-KR6M`. **Eleven are Gate 2 entries**, and the gate stands at 204 of 229 cleared, from 197 of 222 at v0.5.23; `PL-9F3H`, the cut, ships in no release under `PL-KRS6`.
