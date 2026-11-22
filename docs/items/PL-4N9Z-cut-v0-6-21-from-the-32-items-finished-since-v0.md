---
id: PL-4N9Z
title: Cut v0.6.21 from the 32 items finished since v0.6.20
status: done
resource: release-train
added: 2026-11-22
closed: 2026-11-22
pr: 2253
verify: grep -qF '## Current baseline: v0.6.21' ROADMAP.md
---

**Problem.** Cut v0.6.21 from the 32 items finished since v0.6.20

**Record of the cut.** `make release VERSION=0.6.21` stamped 32 items.
`bin/docket status` offered 0.7.0, because Gate 3 has cleared and all 19
Required-scope ids have closed. 0.6.21 is still the patch, because v0.7.0 is
cut only after the owner's test drive (project instructions' Order, and
`PL-49J8`). `#2231` (`PL-0G2P`, `PL-1D3Z`, `PL-B8DL`) merged inside v0.6.20's
tag span after that cut was written, so `docs/releases/v0.6.20.md` gains an
"also inside this tag's span" section pointing to this release.

The cut reported that the apparatus-inflow prediction missed for the week of
2026-11-09 to 11-15 (4 P1 workflow-lane filings). `PL-Z1ZT` already records
that miss, so nothing new was filed.

The `src/anesthesia_sim/core` and `src/anesthesia_sim/data` tree hashes moved
since v0.6.20, and `tools/ast_identity.py v0.6.20 HEAD` exited 1: `PL-HXNL`,
`PL-DQWL`, `PL-P5W1` and `PL-S8FM` changed how a run is copied and what it
refuses. The data change is one sentence of the reference circle system's
provenance note (`PL-Z843`).

**Trajectories.** `/mnt/project-files/release-trajectory/whole_second_traj.py`
recorded both trees (v0.6.20 and this cut's `src/`, extracted with `git
archive`), and `whole_second_compare.py` compared them: 10,935 per-minute
samples, 174,960 formatted readouts, 72 hourly samples of three 24-hour runs
and 271 stops. Every difference is zero, and every stop is at the same
instant. The output is
`/mnt/project-files/release-trajectory/v0.6.21-against-v0.6.20.txt`.

**Documents checked at close.** `ROADMAP.md` (the version table and the
current baseline section), `docs/releases/v0.6.21.md`,
`docs/releases/v0.6.20.md`, `pyproject.toml` and `uv.lock`.
