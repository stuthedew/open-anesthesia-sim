---
id: PL-245L
title: Cut v0.6.20 from the 57 items finished since v0.6.19
status: done
resource: release-train
added: 2026-11-22
closed: 2026-11-22
pr: 2236
verify: grep -qF '## Current baseline: v0.6.20' ROADMAP.md
---

**Problem.** Cut v0.6.20 from the 57 items finished since v0.6.19

**Record of the cut.** The first cut, of 55 items, was green and closed when
`#2223` (Mapleson's MAC at age 40, the gate's last entry `PL-LBVN`) merged. It
changed the stored MAC values, so its baseline prose was false at the tag. The
two unpushed commits were reset, `origin/main` merged, and `make release
VERSION=0.6.20` re-run: it stamped 57 items. After the merge, `bin/docket wave`
read Gate 3 as 182 cleared, 18 deferred and none open, and `bin/docket status`
offered 0.7.0 as the next version, for the first time. 0.6.20 is still the
patch, because the owner test-drives `main` before v0.7.0 is cut.

The `src/anesthesia_sim/core` and `src/anesthesia_sim/data` tree hashes moved
since v0.6.19, and `tools/ast_identity.py v0.6.19 HEAD` exited 1. Apart from
`#2223`, the code changes in `core/` are the section names in refusal messages
after the model document's split, and the capacity checks reading that section
name from one constant (`CAPACITY_SECTION` in `core/validation.py`, `#2222`).

**Trajectories.** `/mnt/project-files/release-trajectory/whole_second_traj.py`
recorded both trees (v0.6.19 and this cut's `src/`, extracted with `git
archive`), and `whole_second_compare.py` compared them: 10,935 per-minute
samples, 174,960 formatted readouts, 72 hourly samples of three 24-hour runs
and 271 stops. Every case opens its dial at the agent's 1 MAC, so the
fractions moved. `model_mac_ratio.py` beside them checked each fraction
against the v0.6.19 fraction times the agent's MAC ratio (1.8/2.0, 1.17/1.2,
6.6/6.0): the largest departure was 2.9e-14. No MAC-multiple or FA/FI readout
changed, and all 271 stops are at the same instant. The output is
`/mnt/project-files/release-trajectory/v0.6.20-against-v0.6.19.txt`.

**Documents checked at close.** `ROADMAP.md` (the version table, the current
baseline section and the Gate 3 timeline row, whose pointer to the baseline
named v0.6.16 and now names no release), `docs/releases/v0.6.20.md`,
`pyproject.toml` and `uv.lock`.
